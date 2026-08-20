#!/usr/bin/env python3
"""Build a persistent static-background PCD from a ROS2 PointCloud2 bag.

Livox uses a non-repetitive scan pattern, so a wall is not sampled at exactly
the same XYZ position in every frame.  Points are quantized into voxels and a
voxel is considered static only when it is observed in enough distinct frames.
Moving UAV points normally visit a voxel briefly and are therefore excluded.

This tool is intended for a stationary sensor.  It never modifies the bag and
refuses to overwrite an existing PCD.
"""

from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path
import sys

import numpy as np

try:
    import rosbag2_py
    from rclpy.serialization import deserialize_message
    from sensor_msgs.msg import PointCloud2, PointField
except ImportError as exc:
    raise SystemExit(
        "ROS2 Python modules are unavailable. Run:\n"
        "  source /opt/ros/humble/setup.bash"
    ) from exc


FIELD_DTYPES = {
    PointField.INT8: "i1",
    PointField.UINT8: "u1",
    PointField.INT16: "i2",
    PointField.UINT16: "u2",
    PointField.INT32: "i4",
    PointField.UINT32: "u4",
    PointField.FLOAT32: "f4",
    PointField.FLOAT64: "f8",
}
VOXEL_BITS = 21
VOXEL_MASK = (1 << VOXEL_BITS) - 1
VOXEL_OFFSET = 1 << (VOXEL_BITS - 1)


def pointcloud_xyz(message: PointCloud2) -> np.ndarray:
    fields = {field.name: field for field in message.fields}
    missing = {"x", "y", "z"}.difference(fields)
    if missing:
        raise ValueError("PointCloud2 missing fields: " + ", ".join(sorted(missing)))

    byte_order = ">" if message.is_bigendian else "<"
    names = []
    formats = []
    offsets = []
    for name in ("x", "y", "z"):
        field = fields[name]
        if field.datatype not in FIELD_DTYPES or field.count != 1:
            raise ValueError(f"unsupported PointCloud2 field {name}")
        names.append(name)
        formats.append(byte_order + FIELD_DTYPES[field.datatype])
        offsets.append(field.offset)
    dtype = np.dtype(
        {
            "names": names,
            "formats": formats,
            "offsets": offsets,
            "itemsize": message.point_step,
        }
    )
    count = message.width * message.height
    points = np.frombuffer(message.data, dtype=dtype, count=count)
    xyz = np.column_stack((points["x"], points["y"], points["z"]))
    return xyz.astype(np.float32, copy=False)


def pack_voxels(indices: np.ndarray) -> np.ndarray:
    shifted = indices + VOXEL_OFFSET
    if np.any(shifted < 0) or np.any(shifted > VOXEL_MASK):
        raise ValueError("point is outside the supported voxel coordinate range")
    return (
        (shifted[:, 0] << (2 * VOXEL_BITS))
        | (shifted[:, 1] << VOXEL_BITS)
        | shifted[:, 2]
    )


def unpack_voxels(keys: np.ndarray) -> np.ndarray:
    indices = np.empty((len(keys), 3), dtype=np.int64)
    indices[:, 0] = (keys >> (2 * VOXEL_BITS)) & VOXEL_MASK
    indices[:, 1] = (keys >> VOXEL_BITS) & VOXEL_MASK
    indices[:, 2] = keys & VOXEL_MASK
    indices -= VOXEL_OFFSET
    return indices


def write_binary_pcd(path: Path, xyz: np.ndarray) -> None:
    cloud = np.empty(
        len(xyz),
        dtype=[("x", "<f4"), ("y", "<f4"), ("z", "<f4"), ("intensity", "<f4")],
    )
    cloud["x"] = xyz[:, 0]
    cloud["y"] = xyz[:, 1]
    cloud["z"] = xyz[:, 2]
    cloud["intensity"] = 0.0
    header = (
        "# .PCD v0.7 - Point Cloud Data file format\n"
        "VERSION 0.7\n"
        "FIELDS x y z intensity\n"
        "SIZE 4 4 4 4\n"
        "TYPE F F F F\n"
        "COUNT 1 1 1 1\n"
        f"WIDTH {len(cloud)}\n"
        "HEIGHT 1\n"
        "VIEWPOINT 0 0 0 1 0 0 0\n"
        f"POINTS {len(cloud)}\n"
        "DATA binary\n"
    )
    with path.open("xb") as stream:
        stream.write(header.encode("ascii"))
        cloud.tofile(stream)


def build_background(args) -> None:
    if not args.bag.is_dir():
        raise FileNotFoundError(f"ROS2 bag directory not found: {args.bag}")
    if args.output.exists():
        raise FileExistsError(f"output already exists: {args.output}")

    reader = rosbag2_py.SequentialReader()
    reader.open(
        rosbag2_py.StorageOptions(uri=str(args.bag), storage_id="sqlite3"),
        rosbag2_py.ConverterOptions("cdr", "cdr"),
    )
    topics = {item.name: item.type for item in reader.get_all_topics_and_types()}
    if topics.get(args.topic) != "sensor_msgs/msg/PointCloud2":
        raise ValueError(
            f"{args.topic} is not a sensor_msgs/msg/PointCloud2 topic in this bag"
        )

    occupancy: Counter[int] = Counter()
    frame_count = 0
    accepted_points = 0
    roi_min = np.array(args.roi[:3], dtype=np.float32)
    roi_max = np.array(args.roi[3:], dtype=np.float32)

    while reader.has_next():
        topic, serialized, _ = reader.read_next()
        if topic != args.topic:
            continue
        if args.max_frames and frame_count >= args.max_frames:
            break
        message = deserialize_message(serialized, PointCloud2)
        xyz = pointcloud_xyz(message)
        valid = np.all(np.isfinite(xyz), axis=1)
        valid &= np.all(xyz >= roi_min, axis=1)
        valid &= np.all(xyz <= roi_max, axis=1)
        xyz = xyz[valid]
        if len(xyz):
            indices = np.floor(xyz / args.voxel_size).astype(np.int64)
            # One observation per voxel per frame. A dense patch in one frame
            # must not look like a persistent background surface.
            unique_keys = np.unique(pack_voxels(indices))
            occupancy.update(unique_keys.tolist())
            accepted_points += len(xyz)
        frame_count += 1
        if frame_count % 250 == 0:
            print(
                f"Read {frame_count:5d} frames, "
                f"{len(occupancy):7d} occupied voxels...",
                flush=True,
            )

    if not frame_count or not occupancy:
        raise RuntimeError("no usable point-cloud frames were found")

    all_counts = np.fromiter(occupancy.values(), dtype=np.int32)
    print("\nDistinct-frame occupancy summary:")
    for threshold in (2, 5, 10, 20, 40, 80, 120):
        print(f"  >= {threshold:3d} frames: {int(np.count_nonzero(all_counts >= threshold)):8d} voxels")

    selected = np.fromiter(
        (key for key, count in occupancy.items() if count >= args.min_frames),
        dtype=np.int64,
    )
    if not len(selected):
        raise RuntimeError(
            f"no voxel reached --min-frames={args.min_frames}; choose a lower value"
        )
    indices = unpack_voxels(selected)
    # Put each PCD point at its voxel center. The runtime nearest-neighbor
    # threshold accounts for the half-voxel quantization error.
    xyz = (indices.astype(np.float32) + 0.5) * args.voxel_size
    args.output.parent.mkdir(parents=True, exist_ok=True)
    write_binary_pcd(args.output, xyz)

    print("\nBackground map complete:")
    print(f"  bag:             {args.bag}")
    print(f"  frames:          {frame_count}")
    print(f"  accepted points: {accepted_points}")
    print(f"  voxel size:      {args.voxel_size:.3f} m")
    print(f"  min frames:      {args.min_frames}")
    print(f"  background:      {len(xyz)} voxels")
    print(f"  output:          {args.output}")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Build a persistent static-background PCD from a ROS2 bag."
    )
    parser.add_argument("bag", type=Path, help="ROS2 bag directory")
    parser.add_argument("output", type=Path, help="new output .pcd path")
    parser.add_argument("--topic", default="/livox/lidar")
    parser.add_argument("--voxel-size", type=float, default=0.10, metavar="METERS")
    parser.add_argument(
        "--min-frames",
        type=int,
        default=20,
        help="minimum number of distinct frames that must observe a static voxel",
    )
    parser.add_argument(
        "--max-frames", type=int, default=0, help="0 means process the whole bag"
    )
    parser.add_argument(
        "--roi",
        type=float,
        nargs=6,
        default=[-50.0, -50.0, -5.0, 50.0, 50.0, 30.0],
        metavar=("XMIN", "YMIN", "ZMIN", "XMAX", "YMAX", "ZMAX"),
    )
    args = parser.parse_args()
    if args.voxel_size <= 0:
        parser.error("--voxel-size must be greater than zero")
    if args.min_frames <= 0:
        parser.error("--min-frames must be greater than zero")
    if any(lo >= hi for lo, hi in zip(args.roi[:3], args.roi[3:])):
        parser.error("each ROI minimum must be smaller than its maximum")
    return args


def main() -> int:
    args = parse_args()
    try:
        build_background(args)
    except (FileExistsError, FileNotFoundError, RuntimeError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
