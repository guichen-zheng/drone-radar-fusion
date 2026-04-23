"""
web_dashboard/app.py
Flask + SocketIO 后端：
  - 订阅 /fusion/final_result  → 推送无人机坐标到前端地图（光标 + 高度）
  - 订阅 /fusion/warn_json     → 推送报警通知到前端弹窗
  - 订阅 /camera/debug_image   → 推送实时监控画面（base64 JPEG）
  - 接收前端 set_sensor_pose   → 发布 /web_dashboard/sensor_pose 给 fusion 节点
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
from ament_index_python.packages import get_package_share_directory
import os

from std_msgs.msg import String
from sensor_msgs.msg import Image
from interface.msg import DroneDetectArray

import cv2
import numpy as np
from cv_bridge import CvBridge

# ─────────────────────────────────────────────────────────────────────────────
_share_dir = get_package_share_directory('web_dashboard')
app    = Flask(__name__, template_folder=os.path.join(_share_dir, 'templates'))
sio    = SocketIO(app, cors_allowed_origins="*", async_mode="threading")
bridge = CvBridge()

# 当前传感器位姿状态，供新客户端连接时恢复显示
_sensor_pose = None   # {"lat": float, "lng": float, "heading": float}
_ros_node    = None   # WebDashboardNode 全局引用，供 SocketIO 回调发布话题


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

        # 发布传感器位姿到 fusion 节点
        self.pub_sensor_pose_ = self.create_publisher(
            String, "/web_dashboard/sensor_pose", 10)

        self.get_logger().info("[WebDashboard] ROS2 节点已启动，推送地址：http://0.0.0.0:5000")

        # 传感器连接状态（最近 3 秒内有无数据）
        self._radar_last_time  = 0.0
        self._camera_last_time = 0.0
        self._radar_ok  = False
        self._camera_ok = False
        self.create_timer(2.0, self._check_sensor_status)

    # ── ROS2 回调 → SocketIO 推送 ─────────────────────────
    def _on_final_result(self, msg: DroneDetectArray):
        self._radar_last_time = time.time()
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
        self._camera_last_time = time.time()
        try:
            cv_img = bridge.imgmsg_to_cv2(msg, "bgr8")
            # 压缩为 JPEG base64（降低带宽压力）
            _, buf = cv2.imencode(".jpg", cv_img, [cv2.IMWRITE_JPEG_QUALITY, 60])
            b64 = base64.b64encode(buf).decode("utf-8")
            sio.emit("camera_frame", {"data": b64})
        except Exception as e:
            self.get_logger().warn(f"[WebDashboard] 图像推送失败：{e}")


    def _check_sensor_status(self):
        now = time.time()
        radar_ok  = (now - self._radar_last_time)  < 3.0
        camera_ok = (now - self._camera_last_time) < 3.0
        if radar_ok != self._radar_ok or camera_ok != self._camera_ok:
            self._radar_ok  = radar_ok
            self._camera_ok = camera_ok
            sio.emit('sensor_status', {'radar': radar_ok, 'camera': camera_ok})


# ── SocketIO 传感器位姿事件 ───────────────────────────────────────────────────

@sio.on('set_sensor_pose')
def on_set_sensor_pose(data):
    """
    接收前端发来的传感器位姿：{"lat": float, "lng": float, "heading": float}
    发布到 /web_dashboard/sensor_pose 供 fusion_manager 更新坐标转换。
    """
    global _sensor_pose, _ros_node
    try:
        lat     = float(data['lat'])
        lng     = float(data['lng'])
        heading = float(data['heading'])
    except (KeyError, TypeError, ValueError) as e:
        print(f"[WebDashboard] set_sensor_pose 参数错误: {e}")
        return

    _sensor_pose = {"lat": lat, "lng": lng, "heading": heading}

    if _ros_node is not None:
        msg = String()
        msg.data = json.dumps(_sensor_pose)
        _ros_node.pub_sensor_pose_.publish(msg)
        _ros_node.get_logger().info(
            f"[WebDashboard] 传感器位姿已发布: lat={lat:.6f} lng={lng:.6f} heading={heading:.1f}°")

    # 广播给所有已连接客户端，同步多端显示
    sio.emit('sensor_pose_current', _sensor_pose)


@sio.on('request_sensor_pose')
def on_request_sensor_pose():
    """新客户端连接时请求当前位姿，用于恢复地图上的传感器箭头。"""
    if _sensor_pose is not None:
        sio.emit('sensor_pose_current', _sensor_pose)


@sio.on('request_sensor_status')
def on_request_sensor_status():
    """新客户端连接时请求雷达/相机当前连接状态。"""
    if _ros_node is not None:
        sio.emit('sensor_status', {
            'radar':  _ros_node._radar_ok,
            'camera': _ros_node._camera_ok,
        })


# ─────────────────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")


# ─────────────────────────────────────────────────────────────────────────────
def spin_ros(node):
    rclpy.spin(node)


def main():
    global _ros_node
    rclpy.init()
    node = WebDashboardNode()
    _ros_node = node   # 保存全局引用供 SocketIO 回调使用

    # ROS2 spin 在独立线程运行
    ros_thread = threading.Thread(target=spin_ros, args=(node,), daemon=True)
    ros_thread.start()

    # Flask + SocketIO 在主线程运行
    sio.run(app, host="0.0.0.0", port=5000, debug=False)

    rclpy.shutdown()


if __name__ == "__main__":
    main()
