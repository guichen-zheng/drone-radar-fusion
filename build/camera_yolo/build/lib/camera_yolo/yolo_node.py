"""
yolo_node.py — Python ROS2 节点，通过 subprocess 桥接 conda 环境跑 YOLO

为什么不直接用 camera_vision (C++) 包：系统 OpenCV 4.5.4 的 DNN 模块解析新版
YOLOv8 ONNX 时会触发 shape_utils 的 total() 断言崩溃，与 opset 11/12/17 都不兼容。
绕过方法：让 ROS 节点（系统 Python 3.10 + rclpy）跑在系统 Python，把图像通过 stdin
管道送给 conda 环境的 Python（含 ultralytics + 较新 cv2），后者跑推理后把检测结果
用 JSON 通过 stdout 返回。

订阅：/hik_camera/image_raw (sensor_msgs/Image)
发布：/camera/detect_result (interface/DroneDetectArray)
       /camera/debug_image  (sensor_msgs/Image，绘制 bbox 调试图)
"""
import os
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


class YoloNode(Node):
    def __init__(self):
        super().__init__("yolo_detector")

        self.declare_parameter("model_path", "model/ONNX/yolo_drone.onnx")
        self.declare_parameter("conf_thresh", 0.25)
        self.declare_parameter("input_size", 640)
        self.declare_parameter(
            "conda_python", "/home/guichen/miniconda3/envs/yolov8/bin/python"
        )
        self.declare_parameter("image_topic", "/hik_camera/image_raw")

        model_path   = self.get_parameter("model_path").get_parameter_value().string_value
        conf         = self.get_parameter("conf_thresh").get_parameter_value().double_value
        imgsz        = self.get_parameter("input_size").get_parameter_value().integer_value
        conda_python = self.get_parameter("conda_python").get_parameter_value().string_value
        image_topic  = self.get_parameter("image_topic").get_parameter_value().string_value

        worker_script = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "yolo_worker.py"
        )
        if not os.path.exists(worker_script):
            self.get_logger().error(f"[YOLO] worker 脚本不存在: {worker_script}")
            raise RuntimeError("worker not found")
        if not os.path.exists(conda_python):
            self.get_logger().error(
                f"[YOLO] conda Python 不存在: {conda_python}\n"
                f"请安装 yolov8 环境，或在 launch 里用 conda_python 参数覆盖路径"
            )
            raise RuntimeError("conda python not found")

        self.proc = subprocess.Popen(
            [conda_python, worker_script, model_path, str(conf), str(imgsz)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=0,
        )
        self._stdin_lock = threading.Lock()

        threading.Thread(target=self._pump_stderr, daemon=True).start()

        self.bridge = CvBridge()
        self.sub = self.create_subscription(
            Image, image_topic, self.on_image, 10
        )
        self.pub_det = self.create_publisher(
            DroneDetectArray, "/camera/detect_result", 10
        )
        self.pub_dbg = self.create_publisher(
            Image, "/camera/debug_image", 10
        )

        self.get_logger().info(
            f"[YOLO] 节点已启动（conda subprocess）\n"
            f"  conda_python = {conda_python}\n"
            f"  worker = {worker_script}\n"
            f"  model = {model_path}\n"
            f"  conf  = {conf}\n"
            f"  image_topic = {image_topic}"
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
            self.get_logger().info(
                f"[YOLO] 收到第 {self._frame_count} 帧 ({msg.width}x{msg.height})"
            )

        if self.proc.poll() is not None:
            self.get_logger().error("[YOLO] worker 已退出")
            return

        try:
            cv_img = self.bridge.imgmsg_to_cv2(msg, "bgr8")
        except Exception as e:
            self.get_logger().warn(f"[YOLO] 图像转换失败: {e}")
            return

        ok, jpeg = cv2.imencode(".jpg", cv_img, [cv2.IMWRITE_JPEG_QUALITY, 85])
        if not ok:
            return
        jpeg_bytes = jpeg.tobytes()

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

        arr = DroneDetectArray()
        arr.header = msg.header
        n_dets = len(data.get("detections", []))
        if self._frame_count <= 3 or n_dets > 0 or self._frame_count % 30 == 0:
            self.get_logger().info(
                f"[YOLO] 推理完成第 {self._frame_count} 帧，检测到 {n_dets} 个目标"
            )
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

        # 始终发 debug 图（即使没检测到也发原图），方便 RViz 验证 pipeline 活着
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
