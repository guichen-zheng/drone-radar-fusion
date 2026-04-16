#!/usr/bin/env python3
"""
config/calib_tool/calib_interactive.py
相机-激光雷达外参手动标定工具（参考原库五点标定逻辑）

使用方法：
  1. 确保 hik_camera 和 livox_driver 节点已运行
  2. ros2 run web_dashboard calib_interactive
     （或直接：python3 calib_interactive.py）
  3. 在弹出窗口中用键盘微调外参，满意后按 S 保存到 out_matrix.yaml

键位说明：
  W/S  → 平移 T_z +/-       (前后)
  A/D  → 平移 T_x +/-       (左右)
  Q/E  → 平移 T_y +/-       (上下)
  I/K  → 旋转 Pitch +/-     (俯仰)
  J/L  → 旋转 Yaw   +/-     (偏航)
  U/O  → 旋转 Roll  +/-     (横滚)
  +/-  → 调整步长
  R    → 重置为单位矩阵
  S    → 保存到 config/out_matrix.yaml
  ESC  → 退出
"""

import rclpy
from rclpy.node import Node
import numpy as np
import cv2
import yaml
import os

from sensor_msgs.msg import Image, PointCloud2
from cv_bridge import CvBridge
import sensor_msgs_py.point_cloud2 as pc2


class CalibTool(Node):
    def __init__(self):
        super().__init__("calib_tool")

        self.bridge = CvBridge()
        self.latest_image = None
        self.latest_cloud = None

        # 外参初始值（4×4，从 out_matrix.yaml 加载或单位矩阵）
        self.T = np.eye(4, dtype=np.float64)
        self._load_existing_calib()

        # 相机内参（从 out_matrix.yaml 加载）
        self.K = np.array([[1200., 0., 960.],
                           [0., 1200., 540.],
                           [0., 0., 1.]], dtype=np.float64)
        self.dist = np.zeros(5)

        # 步长
        self.t_step = 0.01   # 米/次
        self.r_step = 0.005  # 弧度/次

        # 订阅
        self.create_subscription(Image, "/hik_camera/image_raw",
                                 self._on_image, 10)
        self.create_subscription(PointCloud2, "/livox/lidar",
                                 self._on_cloud, 10)

        # 定时刷新显示
        self.create_timer(0.05, self._render)

        self.get_logger().info("[CalibTool] 标定工具已启动，按键说明请查看脚本顶部注释")

    # ── 订阅回调 ───────────────────────────────────────────
    def _on_image(self, msg):
        try:
            self.latest_image = self.bridge.imgmsg_to_cv2(msg, "bgr8")
        except Exception:
            pass

    def _on_cloud(self, msg):
        pts = []
        for p in pc2.read_points(msg, field_names=("x", "y", "z"), skip_nans=True):
            pts.append([p[0], p[1], p[2]])
        self.latest_cloud = np.array(pts, dtype=np.float32) if pts else None

    # ── 渲染：将点云投影到图像上 ──────────────────────────
    def _render(self):
        if self.latest_image is None:
            return

        vis = self.latest_image.copy()

        if self.latest_cloud is not None:
            self._project_cloud(vis)

        # 显示当前外参数值
        tx, ty, tz = self.T[0,3], self.T[1,3], self.T[2,3]
        r = cv2.Rodrigues(self.T[:3, :3])[0].flatten()
        info = [
            f"T: ({tx:.3f}, {ty:.3f}, {tz:.3f}) m",
            f"R: ({np.degrees(r[0]):.2f}, {np.degrees(r[1]):.2f}, {np.degrees(r[2]):.2f}) deg",
            f"Step T:{self.t_step:.3f}m  R:{np.degrees(self.r_step):.2f}deg",
            "S=Save  R=Reset  ESC=Exit",
        ]
        for i, txt in enumerate(info):
            cv2.putText(vis, txt, (10, 25 + i*22),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 1)

        # 缩放显示（高分辨率相机可能太大）
        h, w = vis.shape[:2]
        if w > 1280:
            vis = cv2.resize(vis, (1280, int(h * 1280 / w)))

        cv2.imshow("Calib Tool - Camera + LiDAR", vis)
        key = cv2.waitKey(1) & 0xFF
        self._handle_key(key)

    def _project_cloud(self, img):
        """将 LiDAR 点云通过当前外参投影到图像上，按距离着色"""
        pts_h = np.hstack([self.latest_cloud,
                           np.ones((len(self.latest_cloud), 1))])  # Nx4
        pts_cam = (self.T @ pts_h.T).T[:, :3]  # 变换到相机坐标系

        # 过滤相机前方的点
        mask = pts_cam[:, 2] > 0.5
        pts_cam = pts_cam[mask]
        if len(pts_cam) == 0:
            return

        # 投影到像素
        pts_img, _ = cv2.projectPoints(
            pts_cam.astype(np.float32),
            np.zeros(3), np.zeros(3),
            self.K, self.dist)
        pts_img = pts_img.reshape(-1, 2).astype(int)

        h, w = img.shape[:2]
        dists = np.linalg.norm(pts_cam, axis=1)
        d_min, d_max = dists.min(), max(dists.max(), 1.0)

        for (px, py), d in zip(pts_img, dists):
            if 0 <= px < w and 0 <= py < h:
                # 距离近=绿，远=红
                ratio = (d - d_min) / (d_max - d_min)
                color = (0, int(255*(1-ratio)), int(255*ratio))
                cv2.circle(img, (px, py), 2, color, -1)

    # ── 键盘控制 ───────────────────────────────────────────
    def _handle_key(self, key):
        if key == 255 or key == -1:
            return

        delta_t = np.eye(4)
        delta_r = np.eye(3)

        if   key == ord('w'): delta_t[2,3] =  self.t_step
        elif key == ord('s') and key != ord('S'): pass  # 's' 用于平移 z-
        elif key == ord('s'): delta_t[2,3] = -self.t_step
        elif key == ord('a'): delta_t[0,3] = -self.t_step
        elif key == ord('d'): delta_t[0,3] =  self.t_step
        elif key == ord('q'): delta_t[1,3] =  self.t_step
        elif key == ord('e'): delta_t[1,3] = -self.t_step
        # 旋转（绕 x/y/z 轴）
        elif key == ord('i'): delta_r = self._rot_x( self.r_step)
        elif key == ord('k'): delta_r = self._rot_x(-self.r_step)
        elif key == ord('j'): delta_r = self._rot_y( self.r_step)
        elif key == ord('l'): delta_r = self._rot_y(-self.r_step)
        elif key == ord('u'): delta_r = self._rot_z( self.r_step)
        elif key == ord('o'): delta_r = self._rot_z(-self.r_step)
        # 步长调整
        elif key == ord('='): self.t_step = min(self.t_step * 2, 1.0)
        elif key == ord('-'): self.t_step = max(self.t_step / 2, 0.001)
        # 特殊操作
        elif key == ord('R') or key == ord('r'): self.T = np.eye(4)
        elif key == ord('S'): self._save_calib()
        elif key == 27:  # ESC
            cv2.destroyAllWindows()
            rclpy.shutdown()
            return

        delta_t[:3, :3] = delta_r
        self.T = delta_t @ self.T

    @staticmethod
    def _rot_x(a):
        return np.array([[1,0,0],[0,np.cos(a),-np.sin(a)],[0,np.sin(a),np.cos(a)]])
    @staticmethod
    def _rot_y(a):
        return np.array([[np.cos(a),0,np.sin(a)],[0,1,0],[-np.sin(a),0,np.cos(a)]])
    @staticmethod
    def _rot_z(a):
        return np.array([[np.cos(a),-np.sin(a),0],[np.sin(a),np.cos(a),0],[0,0,1]])

    # ── 保存/加载 ──────────────────────────────────────────
    def _save_calib(self):
        out_path = os.path.join(os.path.dirname(__file__),
                                "../../config/out_matrix.yaml")
        out_path = os.path.normpath(out_path)
        data = {
            "camera_matrix": {
                "rows": 3, "cols": 3,
                "data": self.K.flatten().tolist()
            },
            "dist_coeffs": {
                "rows": 1, "cols": 5,
                "data": self.dist.tolist()
            },
            "T_cam_lidar": {
                "rows": 4, "cols": 4,
                "data": self.T.flatten().tolist()
            }
        }
        with open(out_path, "w") as f:
            yaml.dump(data, f, default_flow_style=False)
        self.get_logger().info(f"[CalibTool] 外参已保存：{out_path}")

    def _load_existing_calib(self):
        path = os.path.join(os.path.dirname(__file__),
                            "../../config/out_matrix.yaml")
        path = os.path.normpath(path)
        if not os.path.exists(path):
            return
        try:
            with open(path) as f:
                cfg = yaml.safe_load(f)
            T_data = cfg["T_cam_lidar"]["data"]
            self.T = np.array(T_data, dtype=np.float64).reshape(4, 4)
            K_data = cfg["camera_matrix"]["data"]
            self.K = np.array(K_data, dtype=np.float64).reshape(3, 3)
            self.get_logger().info("[CalibTool] 已加载现有标定文件")
        except Exception as e:
            self.get_logger().warn(f"[CalibTool] 加载标定文件失败：{e}")


def main():
    rclpy.init()
    node = CalibTool()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        cv2.destroyAllWindows()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
