"""
web_dashboard/app.py
Flask + SocketIO 后端：
  - 订阅 /fusion/final_result  → 推送无人机坐标到前端地图（光标 + 高度）
  - 订阅 /fusion/warn_json     → 推送报警通知到前端弹窗
  - 订阅 /camera/debug_image   → 推送实时监控画面（base64 JPEG）
运行方式（需在 ROS2 环境中）：
  ros2 run web_dashboard web_dashboard_node
或直接：
  python3 app.py
"""

import rclpy
from rclpy.node import Node
import threading
import base64
import json
import time

from flask import Flask, render_template
from flask_socketio import SocketIO

from std_msgs.msg import String
from sensor_msgs.msg import Image
from interface.msg import DroneDetectArray

import cv2
import numpy as np
from cv_bridge import CvBridge

# ─────────────────────────────────────────────────────────────────────────────
app    = Flask(__name__)
sio    = SocketIO(app, cors_allowed_origins="*", async_mode="threading")
bridge = CvBridge()


class WebDashboardNode(Node):
    def __init__(self):
        super().__init__("web_dashboard_node")

        # 订阅融合最终结果
        self.create_subscription(
            DroneDetectArray, "/fusion/final_result",
            self._on_final_result, 10)

        # 订阅 JSON 报警字符串
        self.create_subscription(
            String, "/fusion/warn_json",
            self._on_warn_json, 10)

        # 订阅相机调试图像（可选，占带宽）
        self.create_subscription(
            Image, "/camera/debug_image",
            self._on_debug_image, 10)

        self.get_logger().info("[WebDashboard] ROS2 节点已启动，推送地址：http://0.0.0.0:5000")

    # ── ROS2 回调 → SocketIO 推送 ─────────────────────────
    def _on_final_result(self, msg: DroneDetectArray):
        drones = []
        for d in msg.drones:
            drones.append({
                "id":         d.drone_id,
                "x":          round(d.x, 2),
                "y":          round(d.y, 2),
                "z":          round(d.z, 2),          # 高度（米）
                "lat":        round(d.lat, 7),         # 纬度（WGS84，由 fusion 填入）
                "lng":        round(d.lng, 7),         # 经度
                "vx":         round(d.vx, 2),
                "vy":         round(d.vy, 2),
                "vz":         round(d.vz, 2),
                "confidence": round(d.confidence, 2),
                "label":      d.label,
            })
        sio.emit("drone_update", {"drones": drones})

    def _on_warn_json(self, msg: String):
        try:
            data = json.loads(msg.data)
            sio.emit("drone_warn", data)
        except json.JSONDecodeError:
            pass

    def _on_debug_image(self, msg: Image):
        try:
            cv_img = bridge.imgmsg_to_cv2(msg, "bgr8")
            # 压缩为 JPEG base64（降低带宽压力）
            _, buf = cv2.imencode(".jpg", cv_img, [cv2.IMWRITE_JPEG_QUALITY, 60])
            b64 = base64.b64encode(buf).decode("utf-8")
            sio.emit("camera_frame", {"data": b64})
        except Exception as e:
            self.get_logger().warn(f"[WebDashboard] 图像推送失败：{e}")


# ─────────────────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")


# ─────────────────────────────────────────────────────────────────────────────
def spin_ros(node):
    rclpy.spin(node)


def main():
    rclpy.init()
    node = WebDashboardNode()

    # ROS2 spin 在独立线程运行
    ros_thread = threading.Thread(target=spin_ros, args=(node,), daemon=True)
    ros_thread.start()

    # Flask + SocketIO 在主线程运行
    sio.run(app, host="0.0.0.0", port=5000, debug=False)

    rclpy.shutdown()


if __name__ == "__main__":
    main()
