"""
simulation/sim_bridge.py

仿真桥接节点：
  - 10 Hz 定时计算无人机圆周轨迹（雷达坐标系）
  - 调用 /gazebo/set_entity_state 服务同步移动 Gazebo 中的无人机模型
  - 发布 /radar/detect       → 供 fusion_manager 使用
  - 发布 /camera/detect_result → 供 fusion_manager 使用
  - 发布 /sim/drone_visual   → RViz 无人机 3D 标记
  - 发布 /sim/sensor_visual  → RViz 传感器云台 3D 标记（1Hz，静态）

轨迹（雷达坐标系，x=前 y=左 z=上）：
  x(t) = R·cos(ω·t),  y(t) = R·sin(ω·t),  z = H
"""

import math
import rclpy
from rclpy.node import Node

from geometry_msgs.msg import Pose, Point, Quaternion, Vector3
from std_msgs.msg import ColorRGBA, Header
from visualization_msgs.msg import Marker, MarkerArray
from gazebo_msgs.srv import SetEntityState
from gazebo_msgs.msg import EntityState

from interface.msg import DroneDetect, DroneDetectArray


# ── 辅助函数 ────────────────────────────────────────────────────────────────────
def _color(r, g, b, a=1.0):
    c = ColorRGBA()
    c.r = float(r); c.g = float(g); c.b = float(b); c.a = float(a)
    return c

def _scale(x, y, z):
    s = Vector3()
    s.x = float(x); s.y = float(y); s.z = float(z)
    return s

def _pose(x, y, z, qx=0., qy=0., qz=0., qw=1.):
    p = Pose()
    p.position.x = float(x); p.position.y = float(y); p.position.z = float(z)
    p.orientation.x = float(qx); p.orientation.y = float(qy)
    p.orientation.z = float(qz); p.orientation.w = float(qw)
    return p


class SimBridge(Node):
    def __init__(self):
        super().__init__('sim_bridge')

        # ── 轨迹参数 ──────────────────────────────────────────────────────────
        self.radius     = self.declare_parameter('radius',  20.0).value
        self.height     = self.declare_parameter('height',  20.0).value
        self.period     = self.declare_parameter('period',  40.0).value
        self.drone_name = self.declare_parameter('drone_model_name', 'drone').value

        # ── 仿真标定参数（与 sim_calib.yaml 一致） ────────────────────────────
        self.fx = 1000.0; self.fy = 1000.0
        self.cx = 1224.0; self.cy = 1024.0

        # ── 发布者 ────────────────────────────────────────────────────────────
        self.pub_radar      = self.create_publisher(DroneDetectArray, '/radar/detect',          10)
        self.pub_camera     = self.create_publisher(DroneDetectArray, '/camera/detect_result',  10)
        self.pub_drone_vis  = self.create_publisher(MarkerArray,      '/sim/drone_visual',      10)
        self.pub_sensor_vis = self.create_publisher(MarkerArray,      '/sim/sensor_visual',     10)

        # ── Gazebo SetEntityState 服务客户端 ─────────────────────────────────
        self.gazebo_cli = self.create_client(SetEntityState, '/gazebo/set_entity_state')
        if not self.gazebo_cli.wait_for_service(timeout_sec=12.0):
            self.get_logger().warn(
                '[SimBridge] /gazebo/set_entity_state 不可用，Gazebo 模型不会移动')
            self.gazebo_ok = False
        else:
            self.gazebo_ok = True
            self.get_logger().info('[SimBridge] Gazebo 服务已连接，无人机将同步移动')

        # ── 定时器 ────────────────────────────────────────────────────────────
        self.t = 0.0
        self.create_timer(0.1, self.step)          # 10 Hz 主循环
        self.create_timer(1.0, self._pub_sensor)   # 1 Hz 传感器静态标记

        self.get_logger().info(
            f'[SimBridge] 启动：R={self.radius}m H={self.height}m T={self.period}s')

    # ── 主循环（10 Hz）────────────────────────────────────────────────────────
    def step(self):
        self.t += 0.1
        omega = 2.0 * math.pi / self.period
        x = self.radius * math.cos(omega * self.t)
        y = self.radius * math.sin(omega * self.t)
        z = self.height

        if self.gazebo_ok:
            self._move_gazebo(x, y, z)

        now = self.get_clock().now().to_msg()
        self._publish_radar(x, y, z, now)
        self._publish_camera(x, y, z, now)
        self._pub_drone_visual(x, y, z, now)

    # ── 雷达检测 ───────────────────────────────────────────────────────────────
    def _publish_radar(self, x, y, z, stamp):
        arr = DroneDetectArray()
        arr.header.stamp    = stamp
        arr.header.frame_id = 'lidar'
        det = DroneDetect()
        det.drone_id = 0; det.x = float(x); det.y = float(y); det.z = float(z)
        det.confidence = 0.9; det.label = 'drone'; det.is_tracked = False
        arr.drones.append(det)
        self.pub_radar.publish(arr)

    # ── 相机检测（投影计算 bbox）───────────────────────────────────────────────
    def _publish_camera(self, x, y, z, stamp):
        xc, yc, zc = -y, -z, x          # 轴变换：雷达→相机
        if zc < 0.5:
            return
        u  = self.fx * xc / zc + self.cx
        v  = self.fy * yc / zc + self.cy
        hw = max(15, int(300.0 / zc))
        arr = DroneDetectArray()
        arr.header.stamp    = stamp
        arr.header.frame_id = 'camera'
        det = DroneDetect()
        det.drone_id = 0
        det.bbox_x = int(u - hw); det.bbox_y = int(v - hw)
        det.bbox_w = hw * 2;      det.bbox_h = hw * 2
        det.confidence = 0.85;    det.label  = 'drone'
        arr.drones.append(det)
        self.pub_camera.publish(arr)

    # ── RViz 无人机可视化标记 ──────────────────────────────────────────────────
    def _pub_drone_visual(self, x, y, z, stamp):
        ma = MarkerArray()
        hdr = Header(); hdr.stamp = stamp; hdr.frame_id = 'lidar'

        def mk(mid, mtype, px, py, pz, sx, sy, sz, r, g, b, a=1.0, qx=0.,qy=0.,qz=0.,qw=1.):
            m = Marker(); m.header = hdr; m.ns = 'drone'; m.id = mid
            m.type = mtype; m.action = Marker.ADD
            m.pose = _pose(px, py, pz, qx, qy, qz, qw)
            m.scale = _scale(sx, sy, sz)
            m.color = _color(r, g, b, a)
            m.lifetime.sec = 1          # 1s 超时自动消失，防止残影
            return m

        CUBE = Marker.CUBE; CYL = Marker.CYLINDER

        # 机身
        ma.markers.append(mk(0, CUBE, x, y, z, 0.28, 0.28, 0.10, 0.2, 0.2, 0.2))

        # 4 条机臂（用细长方体，沿 45° 旋转）
        sq2 = math.sqrt(2) / 2
        for i, (dx, dy) in enumerate([(1,1),(1,-1),(-1,1),(-1,-1)]):
            ax = x + dx*0.14; ay = y + dy*0.14
            qz = sq2 if dx*dy > 0 else -sq2
            ma.markers.append(mk(1+i, CUBE, ax, ay, z+0.01,
                                  0.36, 0.04, 0.04, 0.18, 0.18, 0.18,
                                  qz=qz, qw=sq2))

        # 4 个螺旋桨（白色扁圆柱）
        arm = 0.26
        for i, (dx, dy) in enumerate([(1,1),(1,-1),(-1,1),(-1,-1)]):
            ma.markers.append(mk(5+i, CYL,
                                  x+dx*arm, y+dy*arm, z+0.07,
                                  0.30, 0.30, 0.015, 0.9, 0.9, 0.9, 0.85))

        # 机身底部红色标记（醒目识别）
        ma.markers.append(mk(9, CYL, x, y, z-0.04, 0.08, 0.08, 0.04, 1.0, 0.2, 0.0))

        self.pub_drone_vis.publish(ma)

    # ── RViz 传感器云台标记（静态，1 Hz 发布确保 RViz 重连后可见）─────────────
    def _pub_sensor(self):
        ma = MarkerArray()
        now = self.get_clock().now().to_msg()
        hdr = Header(); hdr.stamp = now; hdr.frame_id = 'lidar'

        def mk(mid, mtype, px, py, pz, sx, sy, sz, r, g, b, a=1.0,
               qx=0., qy=0., qz=0., qw=1.):
            m = Marker(); m.header = hdr; m.ns = 'sensor'; m.id = mid
            m.type = mtype; m.action = Marker.ADD
            m.pose = _pose(px, py, pz, qx, qy, qz, qw)
            m.scale = _scale(sx, sy, sz)
            m.color = _color(r, g, b, a)
            return m

        CUBE = Marker.CUBE; CYL = Marker.CYLINDER; TEXT = Marker.TEXT_VIEW_FACING

        # 主立柱
        ma.markers.append(mk(0, CYL, 0, 0, 0.65, 0.05, 0.05, 1.3, 0.35, 0.35, 0.35))
        # 云台顶板
        ma.markers.append(mk(1, CUBE, 0, 0, 1.32, 0.28, 0.20, 0.04, 0.25, 0.25, 0.25))
        # Livox Avia 雷达（深色矩形，中央）
        ma.markers.append(mk(2, CUBE, 0, 0, 1.40, 0.16, 0.16, 0.06, 0.12, 0.12, 0.12))
        # 雷达橙色标志
        ma.markers.append(mk(3, CUBE, 0.082, 0, 1.40, 0.003, 0.16, 0.06, 1.0, 0.5, 0.0))
        # 相机（黑色圆柱，侧装）
        # 旋转90°使圆柱横向：绕X轴旋转90° → qx=sin45°≈0.707 qw=cos45°≈0.707
        ma.markers.append(mk(4, CYL, 0, 0.13, 1.40, 0.064, 0.064, 0.09,
                              0.1, 0.1, 0.1, qx=0.707, qw=0.707))
        # 镜头蓝色圈
        ma.markers.append(mk(5, CYL, 0, 0.175, 1.40, 0.044, 0.044, 0.005,
                              0.1, 0.1, 0.8, 0.9, qx=0.707, qw=0.707))
        # 三脚架腿 ×3
        legs = [(0, 0.22, 0.9), (0.19, -0.11, 0.9), (-0.19, -0.11, 0.9)]
        for i, (lx, ly, lz) in enumerate(legs):
            ma.markers.append(mk(6+i, CYL, lx, ly, lz*0.5, 0.036, 0.036, lz,
                                  0.3, 0.3, 0.3))
        # 文字标签
        txt = mk(10, TEXT, 0, 0, 1.6, 0.0, 0.0, 0.15, 0.3, 1.0, 0.3)
        txt.text = '传感器'
        ma.markers.append(txt)

        self.pub_sensor_vis.publish(ma)

    # ── 移动 Gazebo 无人机模型 ─────────────────────────────────────────────────
    def _move_gazebo(self, x, y, z):
        req = SetEntityState.Request()
        state = EntityState()
        state.name = self.drone_name
        state.pose = Pose(
            position    = Point(x=float(x), y=float(y), z=float(z)),
            orientation = Quaternion(x=0.0, y=0.0, z=0.0, w=1.0)
        )
        state.reference_frame = 'world'
        req.state = state
        self.gazebo_cli.call_async(req)


def main(args=None):
    rclpy.init(args=args)
    node = SimBridge()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
