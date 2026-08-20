#!/usr/bin/env python3
"""Convert the TIERS ROS1 UAV dataset into a ROS2 bag used by this project.

The TIERS bags contain an RGB image and Livox Avia ``CustomMsg``.  This
converter keeps the useful camera information and ground-truth pose, converts
the Avia points to ``sensor_msgs/msg/PointCloud2``, and writes the input topics
expected by drone-radar-fusion::

  /camera/color/image_raw       -> /hik_camera/image_raw
  /camera/color/camera_info     -> /hik_camera/camera_info
  /avia/livox/lidar             -> /livox/lidar (PointCloud2)
  /vrpn_client_node/tello/pose  -> /tiers/tello/pose

It intentionally reads the ROS1 v2 file itself so ROS1/Noetic and ros1_bridge
are not required on an Ubuntu 22.04 + ROS2 Humble machine.
"""

from __future__ import annotations

import argparse
import array
import bz2
import math
import os
import struct
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO, Dict, Iterator, Mapping, Optional, Tuple

import numpy as np

try:
    import rosbag2_py
    from geometry_msgs.msg import PoseStamped
    from rclpy.serialization import serialize_message
    from sensor_msgs.msg import CameraInfo, Image, PointCloud2, PointField
except ImportError as exc:
    raise SystemExit(
        "ROS2 Python modules are unavailable. Run this first:\n"
        "  source /opt/ros/humble/setup.bash"
    ) from exc


ROS1_MAGIC = b"#ROSBAG V2.0\n"
OP_MSG_DATA = 0x02
OP_FILE_HEADER = 0x03
OP_CHUNK = 0x05
OP_CONNECTION = 0x07

SOURCE_TOPICS = {
    "/avia/livox/lidar",
    "/camera/color/camera_info",
    "/camera/color/image_raw",
    "/vrpn_client_node/tello/pose",
}


def _u32(value: bytes) -> int:
    return struct.unpack("<I", value)[0]


def _u64(value: bytes) -> int:
    return struct.unpack("<Q", value)[0]


def _parse_fields(blob: bytes) -> Dict[str, bytes]:
    fields: Dict[str, bytes] = {}
    offset = 0
    while offset < len(blob):
        if offset + 4 > len(blob):
            raise ValueError("truncated ROS bag header field length")
        length = struct.unpack_from("<I", blob, offset)[0]
        offset += 4
        value = blob[offset : offset + length]
        offset += length
        if len(value) != length or b"=" not in value:
            raise ValueError("invalid ROS bag header field")
        key, raw = value.split(b"=", 1)
        fields[key.decode("utf-8", "replace")] = raw
    return fields


def _read_record(stream: BinaryIO, *, read_data: bool = True):
    length_raw = stream.read(4)
    if not length_raw:
        return None
    if len(length_raw) != 4:
        raise ValueError("truncated ROS bag record header")
    header_length = struct.unpack("<I", length_raw)[0]
    header = _parse_fields(stream.read(header_length))
    data_length_raw = stream.read(4)
    if len(data_length_raw) != 4:
        raise ValueError("truncated ROS bag record data length")
    data_length = struct.unpack("<I", data_length_raw)[0]
    if read_data:
        data = stream.read(data_length)
        if len(data) != data_length:
            raise ValueError("truncated ROS bag record data")
    else:
        stream.seek(data_length, os.SEEK_CUR)
        data = b""
    return header, data


def _record_from_buffer(buffer: bytes, offset: int):
    header_length = struct.unpack_from("<I", buffer, offset)[0]
    offset += 4
    header = _parse_fields(buffer[offset : offset + header_length])
    offset += header_length
    data_length = struct.unpack_from("<I", buffer, offset)[0]
    offset += 4
    data = memoryview(buffer)[offset : offset + data_length]
    offset += data_length
    return header, data, offset


@dataclass(frozen=True)
class Ros1Message:
    topic: str
    timestamp_ns: int
    data: memoryview


class Ros1Bag:
    """Small streaming ROS1 bag v2 reader for the four TIERS topics."""

    def __init__(self, path: Path):
        self.path = path
        self.connections: Dict[int, Tuple[str, str]] = {}
        self.index_pos = 0
        self.start_offset = len(ROS1_MAGIC)
        self._read_index()

    def _read_index(self) -> None:
        with self.path.open("rb") as stream:
            if stream.read(len(ROS1_MAGIC)) != ROS1_MAGIC:
                raise ValueError(f"not a ROS1 bag v2 file: {self.path}")
            record = _read_record(stream)
            if record is None:
                raise ValueError("bag has no file header")
            header, _ = record
            if header.get("op", b"\0")[0] != OP_FILE_HEADER:
                raise ValueError("invalid ROS1 bag file header")
            self.index_pos = _u64(header["index_pos"])
            stream.seek(self.index_pos)
            while True:
                record = _read_record(stream)
                if record is None:
                    break
                header, data = record
                if header.get("op", b"\0")[0] != OP_CONNECTION:
                    continue
                connection_id = _u32(header["conn"])
                topic = header["topic"].decode("utf-8", "replace")
                connection_header = _parse_fields(data)
                message_type = connection_header.get("type", b"")
                self.connections[connection_id] = (
                    topic,
                    message_type.decode("utf-8", "replace"),
                )

    def messages(self) -> Iterator[Ros1Message]:
        wanted_connections = {
            connection_id
            for connection_id, (topic, _) in self.connections.items()
            if topic in SOURCE_TOPICS
        }
        missing = SOURCE_TOPICS.difference(
            topic for topic, _ in self.connections.values()
        )
        if missing:
            print(
                "Warning: bag does not contain: " + ", ".join(sorted(missing)),
                file=sys.stderr,
            )

        with self.path.open("rb") as stream:
            stream.seek(self.start_offset)
            _read_record(stream, read_data=False)  # file header
            while stream.tell() < self.index_pos:
                record = _read_record(stream)
                if record is None:
                    break
                header, compressed = record
                if header.get("op", b"\0")[0] != OP_CHUNK:
                    continue
                compression = header["compression"].decode("ascii")
                if compression == "none":
                    chunk = compressed
                elif compression == "bz2":
                    chunk = bz2.decompress(compressed)
                else:
                    raise ValueError(
                        f"unsupported ROS1 chunk compression {compression!r}; "
                        "TIERS release bags are expected to use 'none'"
                    )

                offset = 0
                while offset < len(chunk):
                    msg_header, msg_data, offset = _record_from_buffer(chunk, offset)
                    if msg_header.get("op", b"\0")[0] != OP_MSG_DATA:
                        continue
                    connection_id = _u32(msg_header["conn"])
                    if connection_id not in wanted_connections:
                        continue
                    seconds, nanoseconds = struct.unpack("<II", msg_header["time"])
                    topic = self.connections[connection_id][0]
                    yield Ros1Message(
                        topic=topic,
                        timestamp_ns=seconds * 1_000_000_000 + nanoseconds,
                        data=msg_data,
                    )


class Cursor:
    def __init__(self, data: memoryview):
        self.data = data
        self.offset = 0

    def unpack(self, fmt: str):
        values = struct.unpack_from(fmt, self.data, self.offset)
        self.offset += struct.calcsize(fmt)
        return values

    def u8(self) -> int:
        return self.unpack("<B")[0]

    def u32(self) -> int:
        return self.unpack("<I")[0]

    def u64(self) -> int:
        return self.unpack("<Q")[0]

    def string(self) -> str:
        length = self.u32()
        value = bytes(self.data[self.offset : self.offset + length])
        self.offset += length
        return value.decode("utf-8", "replace")

    def bytes(self, length: int) -> memoryview:
        value = self.data[self.offset : self.offset + length]
        self.offset += length
        return value


def _read_header(cursor: Cursor):
    cursor.u32()  # ROS1 Header.seq; ROS2 removed this field.
    seconds, nanoseconds = cursor.unpack("<II")
    frame_id = cursor.string()
    return seconds, nanoseconds, frame_id


def _set_header(message, header) -> None:
    seconds, nanoseconds, frame_id = header
    message.header.stamp.sec = seconds
    message.header.stamp.nanosec = nanoseconds
    message.header.frame_id = frame_id


def convert_image(data: memoryview) -> Image:
    cursor = Cursor(data)
    header = _read_header(cursor)
    message = Image()
    _set_header(message, header)
    message.height, message.width = cursor.unpack("<II")
    message.encoding = cursor.string()
    message.is_bigendian = cursor.u8()
    message.step = cursor.u32()
    payload_length = cursor.u32()
    message.data = array.array("B", cursor.bytes(payload_length))
    return message


def convert_camera_info(data: memoryview) -> CameraInfo:
    cursor = Cursor(data)
    header = _read_header(cursor)
    message = CameraInfo()
    _set_header(message, header)
    message.height, message.width = cursor.unpack("<II")
    message.distortion_model = cursor.string()
    distortion_length = cursor.u32()
    message.d = list(cursor.unpack(f"<{distortion_length}d"))
    message.k = list(cursor.unpack("<9d"))
    message.r = list(cursor.unpack("<9d"))
    message.p = list(cursor.unpack("<12d"))
    message.binning_x, message.binning_y = cursor.unpack("<II")
    (
        message.roi.x_offset,
        message.roi.y_offset,
        message.roi.height,
        message.roi.width,
    ) = cursor.unpack("<IIII")
    message.roi.do_rectify = bool(cursor.u8())
    return message


def convert_pose(data: memoryview) -> PoseStamped:
    cursor = Cursor(data)
    header = _read_header(cursor)
    message = PoseStamped()
    _set_header(message, header)
    (
        message.pose.position.x,
        message.pose.position.y,
        message.pose.position.z,
        message.pose.orientation.x,
        message.pose.orientation.y,
        message.pose.orientation.z,
        message.pose.orientation.w,
    ) = cursor.unpack("<7d")
    return message


LIVOX_POINT_DTYPE = np.dtype(
    {
        "names": ("x", "y", "z", "reflectivity"),
        "formats": ("<f4", "<f4", "<f4", "u1"),
        "offsets": (4, 8, 12, 16),
        "itemsize": 19,
    }
)


def convert_livox(data: memoryview) -> PointCloud2:
    cursor = Cursor(data)
    header = _read_header(cursor)
    cursor.u64()  # timebase; each point also has offset_time.
    declared_point_count = cursor.u32()
    cursor.u8()  # lidar_id
    cursor.bytes(3)  # reserved
    array_length = cursor.u32()
    point_count = min(declared_point_count, array_length)
    raw_points = cursor.bytes(array_length * LIVOX_POINT_DTYPE.itemsize)

    points = np.frombuffer(raw_points, dtype=LIVOX_POINT_DTYPE, count=point_count)
    finite = np.isfinite(points["x"]) & np.isfinite(points["y"]) & np.isfinite(points["z"])
    points = points[finite]
    xyzi = np.empty((len(points), 4), dtype="<f4")
    xyzi[:, 0] = points["x"]
    xyzi[:, 1] = points["y"]
    xyzi[:, 2] = points["z"]
    xyzi[:, 3] = points["reflectivity"]

    message = PointCloud2()
    _set_header(message, header)
    message.height = 1
    message.width = len(points)
    message.fields = [
        PointField(name="x", offset=0, datatype=PointField.FLOAT32, count=1),
        PointField(name="y", offset=4, datatype=PointField.FLOAT32, count=1),
        PointField(name="z", offset=8, datatype=PointField.FLOAT32, count=1),
        PointField(name="intensity", offset=12, datatype=PointField.FLOAT32, count=1),
    ]
    message.is_bigendian = False
    message.point_step = 16
    message.row_step = message.point_step * message.width
    message.data = array.array("B", xyzi.tobytes())
    # Non-finite input points were removed above, so every serialized point is valid.
    message.is_dense = True
    return message


CONVERTERS = {
    "/avia/livox/lidar": (
        "/livox/lidar",
        "sensor_msgs/msg/PointCloud2",
        convert_livox,
    ),
    "/camera/color/image_raw": (
        "/hik_camera/image_raw",
        "sensor_msgs/msg/Image",
        convert_image,
    ),
    "/camera/color/camera_info": (
        "/hik_camera/camera_info",
        "sensor_msgs/msg/CameraInfo",
        convert_camera_info,
    ),
    "/vrpn_client_node/tello/pose": (
        "/tiers/tello/pose",
        "geometry_msgs/msg/PoseStamped",
        convert_pose,
    ),
}


def _topic_metadata(name: str, message_type: str):
    return rosbag2_py.TopicMetadata(
        name=name,
        type=message_type,
        serialization_format="cdr",
    )


def convert_bag(input_path: Path, output_path: Path, max_duration: Optional[float]) -> None:
    if not input_path.is_file():
        raise FileNotFoundError(input_path)
    if output_path.exists():
        raise FileExistsError(
            f"output already exists: {output_path}\n"
            "Choose another output directory; existing data is never overwritten."
        )

    reader = Ros1Bag(input_path)
    writer = rosbag2_py.SequentialWriter()
    writer.open(
        rosbag2_py.StorageOptions(uri=str(output_path), storage_id="sqlite3"),
        rosbag2_py.ConverterOptions(
            input_serialization_format="cdr",
            output_serialization_format="cdr",
        ),
    )
    for output_topic, message_type, _ in CONVERTERS.values():
        writer.create_topic(_topic_metadata(output_topic, message_type))

    counts = {output_topic: 0 for output_topic, _, _ in CONVERTERS.values()}
    first_timestamp_ns: Optional[int] = None
    converted = 0
    for source in reader.messages():
        if first_timestamp_ns is None:
            first_timestamp_ns = source.timestamp_ns
        if (
            max_duration is not None
            and source.timestamp_ns - first_timestamp_ns > max_duration * 1_000_000_000
        ):
            break
        output_topic, _, converter = CONVERTERS[source.topic]
        ros2_message = converter(source.data)
        writer.write(output_topic, serialize_message(ros2_message), source.timestamp_ns)
        counts[output_topic] += 1
        converted += 1
        if converted % 250 == 0:
            elapsed = (source.timestamp_ns - first_timestamp_ns) / 1_000_000_000
            print(f"Converted {converted:5d} messages ({elapsed:5.1f}s of bag time)...")

    if not converted:
        raise RuntimeError("no supported messages were found in the input bag")
    print("\nConversion complete:")
    print(f"  input:  {input_path}")
    print(f"  output: {output_path}")
    for topic, count in counts.items():
        print(f"  {count:5d}  {topic}")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Convert a TIERS ROS1 bag for drone-radar-fusion on ROS2 Humble."
    )
    parser.add_argument("input_bag", type=Path, help="TIERS ROS1 .bag file")
    parser.add_argument("output_bag", type=Path, help="new ROS2 bag directory")
    parser.add_argument(
        "--max-duration",
        type=float,
        default=None,
        metavar="SECONDS",
        help="convert only the first N seconds (useful for a quick smoke test)",
    )
    args = parser.parse_args()
    if args.max_duration is not None and args.max_duration <= 0:
        parser.error("--max-duration must be greater than zero")
    return args


def main() -> int:
    args = parse_args()
    try:
        convert_bag(args.input_bag.resolve(), args.output_bag.resolve(), args.max_duration)
    except (FileExistsError, FileNotFoundError, RuntimeError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
