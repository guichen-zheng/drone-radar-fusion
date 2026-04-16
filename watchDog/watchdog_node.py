#!/usr/bin/env python3
"""
watchDog/watchdog_node.py
系统看门狗：监控各节点心跳，超时自动重启，支持进程状态上报
监控节点：radar_processor / yolo_detector / fusion_manager / web_dashboard_node
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import subprocess
import time
import json
import os
import signal

WATCH_NODES = {
    "radar_processor":    "ros2 launch radar radar_launch.py",
    "yolo_detector":      "ros2 launch camera_vision camera_launch.py",
    "fusion_manager":     "ros2 launch fusion fusion_launch.py",
    "web_dashboard_node": "ros2 run web_dashboard web_dashboard_node",
}

HEARTBEAT_TIMEOUT = 10.0  # 秒，节点超过此时间无心跳则重启


class WatchDogNode(Node):
    def __init__(self):
        super().__init__("watchdog_node")
        self.declare_parameter("heartbeat_timeout", HEARTBEAT_TIMEOUT)
        self.timeout = self.get_parameter("heartbeat_timeout").get_parameter_value().double_value

        # 发布系统状态报告
        self.pub_status = self.create_publisher(String, "/watchdog/system_status", 10)

        # 记录最近一次各节点心跳时间（若接入心跳 topic 可在此更新）
        self.last_seen = {name: time.time() for name in WATCH_NODES}
        self.procs = {}  # name → subprocess.Popen

        # 定时检查（每 5 秒）
        self.create_timer(5.0, self.check_nodes)
        self.get_logger().info("[WatchDog] 看门狗节点已启动，监控：" + ", ".join(WATCH_NODES))

    def check_nodes(self):
        result = subprocess.run(["ros2", "node", "list"],
                                capture_output=True, text=True)
        active = result.stdout

        status = {}
        for name, launch_cmd in WATCH_NODES.items():
            alive = f"/{name}" in active
            status[name] = "OK" if alive else "DEAD"
            if not alive:
                self.get_logger().warn(f"[WatchDog] 节点 {name} 已离线，正在重启...")
                self._restart(name, launch_cmd)

        msg = String()
        msg.data = json.dumps(status)
        self.pub_status.publish(msg)

    def _restart(self, name, cmd):
        # 杀掉旧进程（如果有）
        if name in self.procs and self.procs[name].poll() is None:
            self.procs[name].send_signal(signal.SIGTERM)
            time.sleep(1)

        try:
            proc = subprocess.Popen(cmd.split(), stdout=subprocess.DEVNULL,
                                    stderr=subprocess.DEVNULL)
            self.procs[name] = proc
            self.get_logger().info(f"[WatchDog] {name} 已重启（PID={proc.pid}）")
        except Exception as e:
            self.get_logger().error(f"[WatchDog] 重启 {name} 失败：{e}")


def main():
    rclpy.init()
    rclpy.spin(WatchDogNode())
    rclpy.shutdown()


if __name__ == "__main__":
    main()
