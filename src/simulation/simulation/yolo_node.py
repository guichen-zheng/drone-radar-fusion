"""
yolo_node.py — Python ROS2 节点，通过 subprocess 桥接 conda 环境（yolov8）跑 YOLO

为什么不直接用 camera_vision (C++) 包：系统 OpenCV 4.5.4 的 DNN 模块解析新版
YOLOv8 ONNX 时会触发 shape_utils 的 total() 断言崩溃，且与 opset 11/12/17 都不兼容。
绕过方法：让 ROS 节点（Python 3.10 + rclpy）跑在系统 Python，把图像通过 stdin
管道送给 conda 环境的 Python 3.8（含 ultralytics 8.4 + cv2 4.13），后者跑推理后
把检测结果用 JSON 通过 stdout 返回。

订阅：/hik_camera/image_raw (sensor_msgs/Image)
发布：/camera/detect_result (interface/DroneDetectArray)
       /camera/debug_image  (sensor_msgs/Image，绘制 bbox 调试图)
"""
import os
import sys
import struct
import json
import subprocess
import threading

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2

from interface.msg import DroneDetect, DroneDetectArray


CONDA_PYTHON = "/home/guichen/miniconda3/envs/yolov8/bin/python"


class YoloNode(Node):
    def __init__(self):
        super().__init__("yolo_detector")

        self.declare_parameter("model_path", "model/ONNX/yolo_drone.onnx")
        self.declare_parameter("conf_thresh", 0.25)
        self.declare_parameter("input_size", 1280)

        model_path = self.get_parameter("model_path").get_parameter_value().string_value
        conf = self.get_parameter("conf_thresh").get_parameter_value().double_value
        imgsz = self.get_parameter("input_size").get_parameter_value().integer_value

        # 启动 conda 环境的 worker 进程
        worker_script = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "yolo_worker.py"
        )
        if not os.path.exists(worker_script):
            self.get_logger().error(f"[YOLO] worker 脚本不存在: {worker_script}")
            raise RuntimeError("worker not found")
        if not os.path.exists(CONDA_PYTHON):
            self.get_logger().error(f"[YOLO] conda Python 不存在: {CONDA_PYTHON}")
            raise RuntimeError("conda python not found")

        self.proc = subprocess.Popen(
            [CONDA_PYTHON, worker_script, model_path, str(conf), str(imgsz)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=0,
        )
        self._stdin_lock = threading.Lock()

        # 把 worker 的 stderr 转到本节点的日志
        threading.Thread(target=self._pump_stderr, daemon=True).start()

        self.bridge = CvBridge()
        self.sub = self.create_subscription(
            Image, "/hik_camera/image_raw", self.on_image, 10
        )
        self.pub_det = self.create_publisher(
            DroneDetectArray, "/camera/detect_result", 10
        )
        self.pub_dbg = self.create_publisher(
            Image, "/camera/debug_image", 10
        )

        self.get_logger().info(
            f"[YOLO] 节点已启动（conda subprocess），model={model_path} conf={conf}"
        )

    def _pump_stderr(self):
        for line in self.proc.stderr:
            try:
                self.get_logger().info(f"[worker] {line.decode().rstrip()}")
            except Exception:
                pass

    def on_image(self, msg: Image):
        if not hasattr(self, "_frame_count"):
            self._frame_count = 0
        self._frame_count += 1
        if self._frame_count <= 3 or self._frame_count % 30 == 0:
            self.get_logger().info(f"[YOLO] 收到第 {self._frame_count} 帧 ({msg.width}x{msg.height})")

        if self.proc.poll() is not None:
            self.get_logger().error("[YOLO] worker 已退出")
            return

        try:
            cv_img = self.bridge.imgmsg_to_cv2(msg, "bgr8")
        except Exception as e:
            self.get_logger().warn(f"[YOLO] 图像转换失败: {e}")
            return

        # JPEG 编码降带宽
        ok, jpeg = cv2.imencode(".jpg", cv_img, [cv2.IMWRITE_JPEG_QUALITY, 85])
        if not ok:
            return
        jpeg_bytes = jpeg.tobytes()

        # 发送 + 同步等待结果（serial 单线程）
        with self._stdin_lock:
            try:
                self.proc.stdin.write(struct.pack(">I", len(jpeg_bytes)))
                self.proc.stdin.write(jpeg_bytes)
                self.proc.stdin.flush()

                hdr = self._read_exact(self.proc.stdout, 4)
                if hdr is None:
                    self.get_logger().error("[YOLO] worker 断开")
                    return
                n = struct.unpack(">I", hdr)[0]
                payload = self._read_exact(self.proc.stdout, n)
                if payload is None:
                    return
            except (BrokenPipeError, ValueError) as e:
                self.get_logger().error(f"[YOLO] IPC 错误: {e}")
                return

        try:
            data = json.loads(payload.decode("utf-8"))
        except Exception as e:
            self.get_logger().warn(f"[YOLO] JSON 解析失败: {e}")
            return

        # 发布检测结果
        arr = DroneDetectArray()
        arr.header = msg.header
        n_dets = len(data.get("detections", []))
        if self._frame_count <= 3 or n_dets > 0 or self._frame_count % 30 == 0:
            self.get_logger().info(f"[YOLO] 推理完成第 {self._frame_count} 帧，检测到 {n_dets} 个目标")
        for d in data.get("detections", []):
            det = DroneDetect()
            det.bbox_x = int(d["x"])
            det.bbox_y = int(d["y"])
            det.bbox_w = int(d["w"])
            det.bbox_h = int(d["h"])
            det.confidence = float(d["conf"])
            det.label = str(d.get("label", "drone"))
            arr.drones.append(det)
        self.pub_det.publish(arr)

        # 发布调试图（绘制 bbox）
        dbg = cv_img.copy()
        for d in data.get("detections", []):
            x, y, w, h = d["x"], d["y"], d["w"], d["h"]
            cv2.rectangle(dbg, (x, y), (x + w, y + h), (0, 255, 0), 2)
            label = f"{d.get('label', 'drone')} {d['conf']:.2f}"
            cv2.putText(dbg, label, (x, max(15, y - 5)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        try:
            dbg_msg = self.bridge.cv2_to_imgmsg(dbg, "bgr8")
            dbg_msg.header = msg.header
            self.pub_dbg.publish(dbg_msg)
        except Exception:
            pass

    @staticmethod
    def _read_exact(stream, n):
        buf = b""
        while len(buf) < n:
            chunk = stream.read(n - len(buf))
            if not chunk:
                return None
            buf += chunk
        return buf


def main(args=None):
    rclpy.init(args=args)
    node = YoloNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        try:
            node.proc.stdin.write(struct.pack(">I", 0))
            node.proc.stdin.flush()
            node.proc.wait(timeout=2)
        except Exception:
            node.proc.kill()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
