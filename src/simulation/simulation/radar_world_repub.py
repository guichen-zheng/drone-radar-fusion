"""
simulation/radar_world_repub.py

雷达检测坐标系转换中转：lidar 局部坐标 → map 世界坐标

为什么需要：
  云台模式下 lidar frame 跟着 sensor_head 旋转，radar_processor 输出的
  /radar/detect 里 (x, y, z) 是 lidar 局部坐标。fusion 把这些数当世界坐标
  追踪，每当云台转过角度，"同一架无人机"在 lidar 局部坐标里位置就变了，
  fusion 误以为是新目标 → 出现幽灵 track。

  这个节点查 TF（map←lidar），对每个检测的位置/速度向量做坐标变换，
  重发布到一个新 topic。fusion 改订阅这个新 topic 后，无人机数和真实数一致。

实物模式下 lidar 不旋转，TF 是 identity，这个节点的行为退化为透传（无副作用）。

用法（在 sim_launch.py 里）：
  Node(package='simulation', executable='radar_world_repub'),
  # 同时把 radar_processor 的 /radar/detect 重映射到 /radar/detect_lidar
  # 这样 repub 接 /radar/detect_lidar，输出回 /radar/detect 给 fusion 用
"""

import copy
import rclpy
from rclpy.node import Node
from rclpy.time import Time
from interface.msg import DroneDetectArray
from tf2_ros import Buffer, TransformListener, TransformException


def quat_to_rotmat(qx, qy, qz, qw):
    """四元数 (x,y,z,w) → 3×3 旋转矩阵"""
    xx, yy, zz = qx * qx, qy * qy, qz * qz
    xy, xz, yz = qx * qy, qx * qz, qy * qz
    wx, wy, wz = qw * qx, qw * qy, qw * qz
    return (
        (1 - 2 * (yy + zz), 2 * (xy - wz),     2 * (xz + wy)    ),
        (2 * (xy + wz),     1 - 2 * (xx + zz), 2 * (yz - wx)    ),
        (2 * (xz - wy),     2 * (yz + wx),     1 - 2 * (xx + yy)),
    )


class RadarWorldRepub(Node):
    def __init__(self):
        super().__init__('radar_world_repub')

        self.declare_parameter('input_topic',  '/radar/detect_lidar')
        self.declare_parameter('output_topic', '/radar/detect')
        self.declare_parameter('world_frame',  'map')
        self.declare_parameter('drop_if_no_tf', True)

        self.input_topic  = self.get_parameter('input_topic').value
        self.output_topic = self.get_parameter('output_topic').value
        self.world_frame  = self.get_parameter('world_frame').value
        self.drop_if_no_tf = self.get_parameter('drop_if_no_tf').value

        self.buffer   = Buffer()
        self.listener = TransformListener(self.buffer, self)

        self.sub = self.create_subscription(
            DroneDetectArray, self.input_topic, self._on_radar, 10)
        self.pub = self.create_publisher(
            DroneDetectArray, self.output_topic, 10)

        self._warn_cnt = 0
        self.get_logger().info(
            f'[RadarWorldRepub] 已启动：{self.input_topic} '
            f'→ (transform via TF {self.world_frame}←lidar) → {self.output_topic}'
        )

    def _on_radar(self, msg: DroneDetectArray):
        source_frame = msg.header.frame_id or 'lidar'
        # 用最新可用 TF（Time() = latest）。云台运动慢，几十 ms 误差可忽略。
        try:
            tf = self.buffer.lookup_transform(
                self.world_frame, source_frame, Time())
        except TransformException as e:
            self._warn_cnt += 1
            if self._warn_cnt % 30 == 1:
                self.get_logger().warn(
                    f'[RadarWorldRepub] TF {self.world_frame}←{source_frame} '
                    f'不可用（已累计 {self._warn_cnt} 次）: {e}')
            if self.drop_if_no_tf:
                return
            # fallback：identity 透传
            tf = None

        # 构造 4×4 仿射（旋转 R + 平移 t）
        if tf is not None:
            t = tf.transform.translation
            q = tf.transform.rotation
            R = quat_to_rotmat(q.x, q.y, q.z, q.w)
            tx, ty, tz = t.x, t.y, t.z
        else:
            R = ((1, 0, 0), (0, 1, 0), (0, 0, 1))
            tx, ty, tz = 0.0, 0.0, 0.0

        out = DroneDetectArray()
        out.header = msg.header
        out.header.frame_id = self.world_frame   # 已经是世界坐标系下

        for d in msg.drones:
            nd = copy.deepcopy(d)
            # 位置：p_world = R @ p_lidar + t
            nd.x = float(R[0][0]*d.x + R[0][1]*d.y + R[0][2]*d.z + tx)
            nd.y = float(R[1][0]*d.x + R[1][1]*d.y + R[1][2]*d.z + ty)
            nd.z = float(R[2][0]*d.x + R[2][1]*d.y + R[2][2]*d.z + tz)
            # 速度只做旋转，不平移
            nd.vx = float(R[0][0]*d.vx + R[0][1]*d.vy + R[0][2]*d.vz)
            nd.vy = float(R[1][0]*d.vx + R[1][1]*d.vy + R[1][2]*d.vz)
            nd.vz = float(R[2][0]*d.vx + R[2][1]*d.vy + R[2][2]*d.vz)
            # bbox / 置信度 / label 等 2D 信息不变
            out.drones.append(nd)

        self.pub.publish(out)


def main(args=None):
    rclpy.init(args=args)
    node = RadarWorldRepub()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
