std_msgs/Header header

uint32 drone_id          # 对应无人机 ID
float64 x                # 世界坐标 X
float64 y                # 世界坐标 Y
float64 z                # 高度（米）
float64 confidence       # 置信度
string warn_level        # 警告等级："LOW" / "MEDIUM" / "HIGH"
string description       # 报警描述（如 "Drone detected at zone A, height 50m"）
builtin_interfaces/Time detected_at  # 检测时间戳
