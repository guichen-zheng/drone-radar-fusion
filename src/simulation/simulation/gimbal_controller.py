"""
simulation/gimbal_controller.py

云台主动注视控制器（v1.2，雷达静止 + 仅相机旋转，目标锁定防抖）：

  ① 订阅 /radar/detect（已是 map 世界坐标，雷达 360° 全向静止粗检）
  ② 目标锁定机制：一旦选定目标，每帧用空间最近邻在新检测里找它，
     除非丢失超过 lock_loss_timeout 秒才允许重选
  ③ 用速率限制（pan_speed / tilt_speed）追踪期望角度
  ④ 通过 /gazebo/set_entity_state 把 sensor_head（仅相机）旋转到 (pan, tilt)
  ⑤ 发布静态 TF：map → lidar（雷达固定），动态 TF：lidar → camera_optical
     （相机外参随云台转动 → fusion 主动注视投影）
  ⑥ 发布 /gimbal/target Marker 给 RViz 显示当前注视的射线

注：v1 用 set_entity_state 走纯运动学路线，跳过 Gazebo 物理 PID。v2 论文版本会换成
URDF joints + ros2_control。
"""

import math
import time
import rclpy
from rclpy.node import Node

from geometry_msgs.msg import Pose, Point, Quaternion, TransformStamped, Vector3
from std_msgs.msg import ColorRGBA
from visualization_msgs.msg import Marker, MarkerArray
from gazebo_msgs.srv import SetEntityState
from gazebo_msgs.msg import EntityState
from interface.msg import DroneDetectArray

from tf2_ros import TransformBroadcaster, StaticTransformBroadcaster


# ── 数学工具 ───────────────────────────────────────────────────────────────────
def euler_to_quat(roll: float, pitch: float, yaw: float) -> Quaternion:
    """ZYX intrinsic (yaw, pitch, roll) Euler → quaternion (xyzw)"""
    cr, sr = math.cos(roll * 0.5),  math.sin(roll * 0.5)
    cp, sp = math.cos(pitch * 0.5), math.sin(pitch * 0.5)
    cy, sy = math.cos(yaw * 0.5),   math.sin(yaw * 0.5)
    q = Quaternion()
    q.w = cr * cp * cy + sr * sp * sy
    q.x = sr * cp * cy - cr * sp * sy
    q.y = cr * sp * cy + sr * cp * sy
    q.z = cr * cp * sy - sr * sp * cy
    return q


def quat_mul(a: Quaternion, b: Quaternion) -> Quaternion:
    """Hamilton 四元数乘 a⊗b（先按 a 旋转，再在其体坐标系内按 b 旋转）。"""
    q = Quaternion()
    q.w = a.w*b.w - a.x*b.x - a.y*b.y - a.z*b.z
    q.x = a.w*b.x + a.x*b.w + a.y*b.z - a.z*b.y
    q.y = a.w*b.y - a.x*b.z + a.y*b.w + a.z*b.x
    q.z = a.w*b.z + a.x*b.y - a.y*b.x + a.z*b.w
    return q


def clip(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def lidar_to_world(lx, ly, lz, pan, tilt, pivot):
    """把雷达局部坐标 (x_fwd, y_left, z_up) 转到世界坐标。
    云台旋转 = R = Rz(pan) @ Ry(tilt)，整体 sensor_head 位姿 = (pivot, R)。"""
    c_pan,  s_pan  = math.cos(pan),  math.sin(pan)
    c_tilt, s_tilt = math.cos(tilt), math.sin(tilt)
    # R = Rz(pan) @ Ry(tilt)：
    # [c_pan*c_tilt, -s_pan, c_pan*s_tilt]
    # [s_pan*c_tilt,  c_pan, s_pan*s_tilt]
    # [-s_tilt,           0, c_tilt      ]
    wx = c_pan * c_tilt * lx + (-s_pan) * ly + c_pan * s_tilt * lz + pivot[0]
    wy = s_pan * c_tilt * lx +   c_pan  * ly + s_pan * s_tilt * lz + pivot[1]
    wz = (-s_tilt)     * lx +     0     * ly + c_tilt          * lz + pivot[2]
    return wx, wy, wz


class GimbalController(Node):
    def __init__(self):
        super().__init__('gimbal_controller')

        # ── 参数 ────────────────────────────────────────────────────────────
        self.declare_parameter('pivot_x', 0.0)
        self.declare_parameter('pivot_y', 0.0)
        self.declare_parameter('pivot_z', 1.55)
        # 关节限制
        self.declare_parameter('pan_min_deg',  -180.0)
        self.declare_parameter('pan_max_deg',   180.0)
        self.declare_parameter('tilt_min_deg',  -85.0)
        self.declare_parameter('tilt_max_deg',   30.0)
        # 速率限制（°/s）
        self.declare_parameter('pan_speed_deg_per_sec',  60.0)
        self.declare_parameter('tilt_speed_deg_per_sec', 45.0)
        # 目标筛选
        self.declare_parameter('min_target_distance', 5.0)
        # 目标锁定参数
        self.declare_parameter('lock_radius_m',      6.0)  # 同一目标在两帧间最大允许偏移
        self.declare_parameter('lock_loss_timeout',  2.0)  # 连续丢失 N 秒才允许重选
        # 控制频率
        self.declare_parameter('control_rate_hz', 30.0)
        # Gazebo 实体名
        self.declare_parameter('entity_name', 'sensor_head')
        # TF frame 名
        self.declare_parameter('tf_world_frame',  'map')
        self.declare_parameter('tf_lidar_frame',  'lidar')
        self.declare_parameter('tf_camera_frame', 'camera_optical')
        # 相机相对雷达的位置偏移（在 sensor_head 模型坐标系内）
        self.declare_parameter('camera_offset_z', 0.07)

        self.pivot = (
            self.get_parameter('pivot_x').value,
            self.get_parameter('pivot_y').value,
            self.get_parameter('pivot_z').value,
        )
        self.pan_min  = math.radians(self.get_parameter('pan_min_deg').value)
        self.pan_max  = math.radians(self.get_parameter('pan_max_deg').value)
        self.tilt_min = math.radians(self.get_parameter('tilt_min_deg').value)
        self.tilt_max = math.radians(self.get_parameter('tilt_max_deg').value)
        self.pan_speed  = math.radians(self.get_parameter('pan_speed_deg_per_sec').value)
        self.tilt_speed = math.radians(self.get_parameter('tilt_speed_deg_per_sec').value)
        self.min_dist        = self.get_parameter('min_target_distance').value
        self.lock_radius     = self.get_parameter('lock_radius_m').value
        self.lock_loss_timeout = self.get_parameter('lock_loss_timeout').value
        rate_hz = self.get_parameter('control_rate_hz').value
        self.entity_name     = self.get_parameter('entity_name').value
        self.world_frame     = self.get_parameter('tf_world_frame').value
        self.lidar_frame     = self.get_parameter('tf_lidar_frame').value
        self.camera_frame    = self.get_parameter('tf_camera_frame').value
        self.cam_offset_z    = self.get_parameter('camera_offset_z').value

        # ── 状态 ────────────────────────────────────────────────────────────
        self.cur_pan  = 0.0
        self.cur_tilt = 0.0
        self.des_pan  = 0.0
        self.des_tilt = 0.0
        self.has_target = False
        # 目标锁定状态
        self.locked = False
        self.locked_world_pos = None      # (x, y, z) 世界坐标
        self.last_seen_time = 0.0
        self._last_tick = time.monotonic()

        # ── Gazebo 服务客户端 ──────────────────────────────────────────────
        self.gazebo_cli = self.create_client(SetEntityState, '/gazebo/set_entity_state')
        if not self.gazebo_cli.wait_for_service(timeout_sec=10.0):
            self.get_logger().warn(
                '[GimbalController] /gazebo/set_entity_state 不可用，云台不会动')

        # ── TF 广播 ────────────────────────────────────────────────────────
        self.tf_dyn = TransformBroadcaster(self)
        self.tf_static = StaticTransformBroadcaster(self)
        self._publish_static_tf()

        # ── 订阅雷达检测 ────────────────────────────────────────────────────
        self.create_subscription(
            DroneDetectArray, '/radar/detect', self._on_radar, 10)

        # ── 发布注视射线 Marker ───────────────────────────────────────────
        self.pub_target_marker = self.create_publisher(
            MarkerArray, '/gimbal/target', 10)

        # ── 控制定时器 ──────────────────────────────────────────────────────
        self.create_timer(1.0 / rate_hz, self._control_tick)

        self.get_logger().info(
            f'[GimbalController] v1.2（雷达静止 + 仅相机转）已启动。'
            f'pivot={self.pivot} pan_speed={math.degrees(self.pan_speed):.0f}°/s '
            f'tilt_speed={math.degrees(self.tilt_speed):.0f}°/s '
            f'min_dist={self.min_dist}m lock_radius={self.lock_radius}m '
            f'lock_loss={self.lock_loss_timeout}s')

    # ── 静态 TF：map → lidar ───────────────────────────────────────────────
    def _publish_static_tf(self):
        """雷达固定在立柱顶端（世界 pivot 处），与世界坐标轴对齐、永远不动。
        所以 map→lidar 是一个常量 TF：平移=pivot，旋转=单位。"""
        t = TransformStamped()
        t.header.stamp = self.get_clock().now().to_msg()
        t.header.frame_id = self.world_frame
        t.child_frame_id  = self.lidar_frame
        t.transform.translation.x = float(self.pivot[0])
        t.transform.translation.y = float(self.pivot[1])
        t.transform.translation.z = float(self.pivot[2])
        t.transform.rotation = Quaternion(x=0.0, y=0.0, z=0.0, w=1.0)
        self.tf_static.sendTransform(t)

    # ── /radar/detect 回调：检测已是世界坐标（由 radar_world_repub 做了 TF 变换）
    def _on_radar(self, msg: DroneDetectArray):
        now = time.monotonic()

        # 注：现在订阅的 /radar/detect 已是 map 坐标系下的检测（由 radar_world_repub
        # 把 lidar 局部坐标转换过）。直接用 d.x/y/z 作为世界坐标。
        candidates = []
        for d in msg.drones:
            wx, wy, wz = float(d.x), float(d.y), float(d.z)
            # 距离按目标到云台支点的世界欧氏距离算
            dx, dy, dz = wx - self.pivot[0], wy - self.pivot[1], wz - self.pivot[2]
            dist = math.sqrt(dx*dx + dy*dy + dz*dz)
            if dist < self.min_dist:
                continue
            candidates.append((wx, wy, wz, float(d.confidence)))

        if not candidates:
            # 没有任何候选，看 lock 是否超时
            if self.locked and now - self.last_seen_time > self.lock_loss_timeout:
                self.get_logger().info(
                    '[GimbalController] 目标连续丢失 %.1fs，释放锁定' % self.lock_loss_timeout)
                self.locked = False
                self.has_target = False
            return

        # ── 1. 若已锁定，优先在候选里用空间最近邻找回原目标 ──────────────
        chose_locked = False
        if self.locked and self.locked_world_pos is not None:
            lx, ly, lz = self.locked_world_pos
            best = min(candidates,
                       key=lambda c: (c[0]-lx)**2 + (c[1]-ly)**2 + (c[2]-lz)**2)
            d2 = (best[0]-lx)**2 + (best[1]-ly)**2 + (best[2]-lz)**2
            if d2 < self.lock_radius * self.lock_radius:
                # 锁定目标仍然在 → 更新位置
                self.locked_world_pos = (best[0], best[1], best[2])
                self.last_seen_time = now
                chose_locked = True
            elif now - self.last_seen_time > self.lock_loss_timeout:
                # 锁定目标丢失超时 → 解除锁定，下面会重选
                self.locked = False

        # ── 2. 若未锁定，选最高 confidence 作为新目标 ────────────────────
        if not self.locked:
            best = max(candidates, key=lambda c: c[3])
            self.locked_world_pos = (best[0], best[1], best[2])
            self.last_seen_time = now
            self.locked = True
            chose_locked = True
            self.get_logger().info(
                '[GimbalController] 锁定新目标：world=(%.1f, %.1f, %.1f) conf=%.2f' %
                (best[0], best[1], best[2], best[3]))

        # ── 3. 从锁定目标的世界位置 → 期望 pan/tilt ─────────────────────
        if chose_locked:
            dx = self.locked_world_pos[0] - self.pivot[0]
            dy = self.locked_world_pos[1] - self.pivot[1]
            dz = self.locked_world_pos[2] - self.pivot[2]
            self.des_pan  = clip(math.atan2(dy, dx),
                                 self.pan_min, self.pan_max)
            self.des_tilt = clip(-math.atan2(dz, math.hypot(dx, dy)),
                                 self.tilt_min, self.tilt_max)
            self.has_target = True

    # ── 控制循环：限速逼近 + set_entity_state + 动态 TF ───────────────────
    def _control_tick(self):
        now = time.monotonic()
        dt = now - self._last_tick
        self._last_tick = now
        if dt <= 0.0 or dt > 0.5:
            dt = 1.0 / 30.0

        # 限速逼近
        if self.has_target:
            self.cur_pan  = self._step_to(self.cur_pan,  self.des_pan,  self.pan_speed,  dt)
            self.cur_tilt = self._step_to(self.cur_tilt, self.des_tilt, self.tilt_speed, dt)

        # 1) 用 set_entity_state 同步 Gazebo sensor_head 姿态
        req = SetEntityState.Request()
        state = EntityState()
        state.name = self.entity_name
        state.pose = Pose(
            position    = Point(x=float(self.pivot[0]),
                                y=float(self.pivot[1]),
                                z=float(self.pivot[2])),
            orientation = euler_to_quat(0.0, self.cur_tilt, self.cur_pan),
        )
        state.reference_frame = 'world'
        req.state = state
        if self.gazebo_cli.service_is_ready():
            self.gazebo_cli.call_async(req)

        # 2) 发布动态 TF：lidar → camera_optical（相机随云台 pan/tilt 转动）
        #    雷达静止、与世界对齐，所以相机相对雷达的外参 = 云台旋转 ∘ 光学约定。
        #    fusion 用这个动态外参把雷达 3D 点投到当前相机像平面。
        q_pantilt = euler_to_quat(0.0, self.cur_tilt, self.cur_pan)
        # REP-103 光学约定：x=right, y=down, z=fwd → RPY=(-π/2, 0, -π/2)
        q_optical = euler_to_quat(-math.pi / 2.0, 0.0, -math.pi / 2.0)
        # 相机光心相对雷达的平移：模型内 +z 偏移，随云台一起转
        ox, oy, oz = lidar_to_world(
            0.0, 0.0, self.cam_offset_z,
            self.cur_pan, self.cur_tilt, (0.0, 0.0, 0.0))
        t = TransformStamped()
        t.header.stamp = self.get_clock().now().to_msg()
        t.header.frame_id = self.lidar_frame
        t.child_frame_id  = self.camera_frame
        t.transform.translation.x = float(ox)
        t.transform.translation.y = float(oy)
        t.transform.translation.z = float(oz)
        t.transform.rotation = quat_mul(q_pantilt, q_optical)
        self.tf_dyn.sendTransform(t)

        # 3) 发布注视射线 Marker
        self._publish_target_marker()

    @staticmethod
    def _step_to(cur: float, des: float, max_rate: float, dt: float) -> float:
        delta = des - cur
        while delta > math.pi:  delta -= 2.0 * math.pi
        while delta < -math.pi: delta += 2.0 * math.pi
        max_step = max_rate * dt
        if delta >  max_step: delta =  max_step
        if delta < -max_step: delta = -max_step
        return cur + delta

    # ── RViz Marker：从云台支点画一条射线到当前锁定目标（世界坐标）─────
    def _publish_target_marker(self):
        ma = MarkerArray()
        clr = Marker()
        clr.header.frame_id = self.world_frame
        clr.header.stamp = self.get_clock().now().to_msg()
        clr.ns = 'gimbal_target'
        clr.action = Marker.DELETEALL
        ma.markers.append(clr)

        if self.locked and self.locked_world_pos is not None \
                and (time.monotonic() - self.last_seen_time) < 2.0:
            wx, wy, wz = self.locked_world_pos
            line = Marker()
            line.header.frame_id = self.world_frame
            line.header.stamp = self.get_clock().now().to_msg()
            line.ns = 'gimbal_target'
            line.id = 0
            line.type = Marker.LINE_STRIP
            line.action = Marker.ADD
            line.scale = Vector3(x=0.05, y=0.0, z=0.0)
            line.color = ColorRGBA(r=0.0, g=1.0, b=1.0, a=0.9)
            # 起点：云台支点（世界坐标）
            line.points.append(Point(
                x=float(self.pivot[0]),
                y=float(self.pivot[1]),
                z=float(self.pivot[2]),
            ))
            # 终点：锁定目标（世界坐标）
            line.points.append(Point(x=float(wx), y=float(wy), z=float(wz)))
            line.lifetime.sec = 0
            line.lifetime.nanosec = 500_000_000
            ma.markers.append(line)

        self.pub_target_marker.publish(ma)


def main(args=None):
    rclpy.init(args=args)
    node = GimbalController()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
