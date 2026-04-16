std_msgs/Header header

uint32 drone_id          # 无人机唯一 ID（多目标追踪）
float64 x                # 世界坐标 X（米）
float64 y                # 世界坐标 Y（米）
float64 z                # 高度 Z（米）
float64 vx               # X 方向速度（米/秒）
float64 vy               # Y 方向速度（米/秒）
float64 vz               # Z 方向速度（米/秒）
float64 confidence       # 融合置信度（0.0 ~ 1.0）
int32 bbox_x             # 图像 bounding box 左上角 x（像素）
int32 bbox_y             # 图像 bounding box 左上角 y（像素）
int32 bbox_w             # bounding box 宽度（像素）
int32 bbox_h             # bounding box 高度（像素）
string label             # 类别标签（如 "drone"）
bool is_tracked          # 是否处于卡尔曼追踪状态

# 地理坐标（由 fusion 包通过 CoordTransform 填入，供 web_dashboard 使用）
float64 lat              # 纬度（度，WGS84）
float64 lng              # 经度（度，WGS84）
