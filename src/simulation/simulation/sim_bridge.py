"""
simulation/sim_bridge.py

仿真桥接节点：
  - 10 Hz 定时计算无人机圆周轨迹（雷达坐标系）
  - 调用 /gazebo/set_entity_state 服务同步移动 Gazebo 中的无人机模型（视觉）
  - 发布 /radar/detect       → 供 fusion_manager 使用
  - 发布 /camera/detect_result → 供 fusion_manager 使用
  - 两个话题使用同一 timestamp，保证 ApproximateTime 同步器必然对齐

无人机轨迹（雷达坐标系，x=前 y=左 z=上）：
  x(t) = R·cos(ω·t)
  y(t) = R·sin(ω·t)
  z    = H（恒定高度）
  R=20m  H=20m  周期=40s

相机 bbox 计算（使用仿真标定参数）：
  轴变换：x_cam = -y_lid,  y_cam = -z_lid,  z_cam = x_lid
  投影：  u = fx·xc/zc + cx,  v = fy·yc/zc + cy
"""

import math
import rclpy
from rclpy.node import Node

from geometry_msgs.msg import Pose, Point, Quaternion
from gazebo_msgs.srv import SetEntityState
from gazebo_msgs.msg import EntityState

from interface.msg import DroneDetect, DroneDetectArray


class SimBridge(Node):
    def __init__(self):
        super().__init__('sim_bridge')

        # ── 轨迹参数 ──────────────────────────────────────────────────────────
        self.radius  = self.declare_parameter('radius',  20.0).value   # 圆周半径（米）
        self.height  = self.declare_parameter('height',  20.0).value   # 飞行高度（米）
        self.period  = self.declare_parameter('period',  40.0).value   # 圆周周期（秒）
        self.drone_name = self.declare_parameter('drone_model_name', 'drone').value

        # ── 仿真标定参数（与 sim_calib.yaml 一致） ────────────────────────────
        self.fx = 1000.0; self.fy = 1000.0
        self.cx = 1224.0; self.cy = 1024.0

        # ── 发布者 ────────────────────────────────────────────────────────────
        self.pub_radar  = self.create_publisher(DroneDetectArray, '/radar/detect', 10)
        self.pub_camera = self.create_publisher(DroneDetectArray, '/camera/detect_result', 10)

        # ── Gazebo SetEntityState 服务客户端 ─────────────────────────────────
        self.gazebo_cli = self.create_client(SetEntityState, '/gazebo/set_entity_state')
        if not self.gazebo_cli.wait_for_service(timeout_sec=5.0):
            self.get_logger().warn(
                '[SimBridge] /gazebo/set_entity_state 服务不可用，Gazebo 模型不会移动'
                '（检测数据仍正常发布）')
            self.gazebo_ok = False
        else:
            self.gazebo_ok = True
            self.get_logger().info('[SimBridge] Gazebo 服务已连接，无人机模型将同步移动')

        # ── 定时器（10 Hz）───────────────────────────────────────────────────
        self.t = 0.0
        self.create_timer(0.1, self.step)
        self.get_logger().info(
            f'[SimBridge] 启动：半径={self.radius}m 高度={self.height}m 周期={self.period}s')

    # ── 主循环 ─────────────────────────────────────────────────────────────────
    def step(self):
        self.t += 0.1
        omega = 2.0 * math.pi / self.period

        # 雷达坐标系：x=前 y=左 z=上
        x = self.radius * math.cos(omega * self.t)
        y = self.radius * math.sin(omega * self.t)
        z = self.height

        # 1. 同步移动 Gazebo 模型
        if self.gazebo_ok:
            self._move_gazebo(x, y, z)

        now = self.get_clock().now().to_msg()

        # 2. 发布雷达检测
        self._publish_radar(x, y, z, now)

        # 3. 发布相机检测
        self._publish_camera(x, y, z, now)

    # ── 雷达检测发布 ────────────────────────────────────────────────────────────
    def _publish_radar(self, x, y, z, stamp):
        arr = DroneDetectArray()
        arr.header.stamp    = stamp
        arr.header.frame_id = 'lidar'

        det = DroneDetect()
        det.drone_id   = 0
        det.x          = float(x)
        det.y          = float(y)
        det.z          = float(z)
        det.confidence = 0.9
        det.label      = 'drone'
        det.is_tracked = False
        arr.drones.append(det)

        self.pub_radar.publish(arr)

    # ── 相机检测发布（投影计算 bbox） ───────────────────────────────────────────
    def _publish_camera(self, x, y, z, stamp):
        # 轴变换：雷达→相机（x_cam=-y_lid, y_cam=-z_lid, z_cam=x_lid）
        xc = -y
        yc = -z
        zc =  x

        if zc < 0.5:
            return  # 无人机在相机后方，不发布

        # 针孔投影
        u = self.fx * xc / zc + self.cx
        v = self.fy * yc / zc + self.cy

        # bbox 半宽：随距离缩放（300/zc 像素），最小 15px
        hw = max(15, int(300.0 / zc))

        arr = DroneDetectArray()
        arr.header.stamp    = stamp   # 与雷达同 stamp → ApproximateTime 必然对齐
        arr.header.frame_id = 'camera'

        det = DroneDetect()
        det.drone_id   = 0
        det.bbox_x     = int(u - hw)
        det.bbox_y     = int(v - hw)
        det.bbox_w     = hw * 2
        det.bbox_h     = hw * 2
        det.confidence = 0.85
        det.label      = 'drone'
        arr.drones.append(det)

        self.pub_camera.publish(arr)

    # ── 移动 Gazebo 模型 ────────────────────────────────────────────────────────
    def _move_gazebo(self, x, y, z):
        req = SetEntityState.Request()
        state = EntityState()
        state.name = self.drone_name
        state.pose = Pose(
            position   = Point(x=float(x), y=float(y), z=float(z)),
            orientation= Quaternion(x=0.0, y=0.0, z=0.0, w=1.0)
        )
        state.reference_frame = 'world'
        req.state = state
        # 异步调用，不阻塞主循环
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
