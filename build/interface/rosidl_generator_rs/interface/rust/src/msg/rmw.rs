#[cfg(feature = "serde")]
use serde::{Deserialize, Serialize};


#[link(name = "interface__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__interface__msg__DroneDetect() -> *const std::ffi::c_void;
}

#[link(name = "interface__rosidl_generator_c")]
extern "C" {
    fn interface__msg__DroneDetect__init(msg: *mut DroneDetect) -> bool;
    fn interface__msg__DroneDetect__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<DroneDetect>, size: usize) -> bool;
    fn interface__msg__DroneDetect__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<DroneDetect>);
    fn interface__msg__DroneDetect__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<DroneDetect>, out_seq: *mut rosidl_runtime_rs::Sequence<DroneDetect>) -> bool;
}

// Corresponds to interface__msg__DroneDetect
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct DroneDetect {

    // This member is not documented.
    #[allow(missing_docs)]
    pub header: std_msgs::msg::rmw::Header,

    /// 无人机唯一 ID（多目标追踪）
    pub drone_id: u32,

    /// 世界坐标 X（米）
    pub x: f64,

    /// 世界坐标 Y（米）
    pub y: f64,

    /// 高度 Z（米）
    pub z: f64,

    /// X 方向速度（米/秒）
    pub vx: f64,

    /// Y 方向速度（米/秒）
    pub vy: f64,

    /// Z 方向速度（米/秒）
    pub vz: f64,

    /// 融合置信度（0.0 ~ 1.0）
    pub confidence: f64,

    /// 图像 bounding box 左上角 x（像素）
    pub bbox_x: i32,

    /// 图像 bounding box 左上角 y（像素）
    pub bbox_y: i32,

    /// bounding box 宽度（像素）
    pub bbox_w: i32,

    /// bounding box 高度（像素）
    pub bbox_h: i32,

    /// 类别标签（如 "drone"）
    pub label: rosidl_runtime_rs::String,

    /// 是否处于卡尔曼追踪状态
    pub is_tracked: bool,

    /// 地理坐标（由 fusion 包通过 CoordTransform 填入，供 web_dashboard 使用）
    /// 纬度（度，WGS84）
    pub lat: f64,

    /// 经度（度，WGS84）
    pub lng: f64,

}



impl Default for DroneDetect {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !interface__msg__DroneDetect__init(&mut msg as *mut _) {
        panic!("Call to interface__msg__DroneDetect__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for DroneDetect {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { interface__msg__DroneDetect__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { interface__msg__DroneDetect__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { interface__msg__DroneDetect__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for DroneDetect {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for DroneDetect where Self: Sized {
  const TYPE_NAME: &'static str = "interface/msg/DroneDetect";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__interface__msg__DroneDetect() }
  }
}


#[link(name = "interface__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__interface__msg__DroneDetectArray() -> *const std::ffi::c_void;
}

#[link(name = "interface__rosidl_generator_c")]
extern "C" {
    fn interface__msg__DroneDetectArray__init(msg: *mut DroneDetectArray) -> bool;
    fn interface__msg__DroneDetectArray__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<DroneDetectArray>, size: usize) -> bool;
    fn interface__msg__DroneDetectArray__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<DroneDetectArray>);
    fn interface__msg__DroneDetectArray__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<DroneDetectArray>, out_seq: *mut rosidl_runtime_rs::Sequence<DroneDetectArray>) -> bool;
}

// Corresponds to interface__msg__DroneDetectArray
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct DroneDetectArray {

    // This member is not documented.
    #[allow(missing_docs)]
    pub header: std_msgs::msg::rmw::Header,

    /// 当前帧所有检测到的无人机列表
    pub drones: rosidl_runtime_rs::Sequence<super::super::msg::rmw::DroneDetect>,

}



impl Default for DroneDetectArray {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !interface__msg__DroneDetectArray__init(&mut msg as *mut _) {
        panic!("Call to interface__msg__DroneDetectArray__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for DroneDetectArray {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { interface__msg__DroneDetectArray__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { interface__msg__DroneDetectArray__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { interface__msg__DroneDetectArray__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for DroneDetectArray {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for DroneDetectArray where Self: Sized {
  const TYPE_NAME: &'static str = "interface/msg/DroneDetectArray";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__interface__msg__DroneDetectArray() }
  }
}


#[link(name = "interface__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__interface__msg__RadarWarn() -> *const std::ffi::c_void;
}

#[link(name = "interface__rosidl_generator_c")]
extern "C" {
    fn interface__msg__RadarWarn__init(msg: *mut RadarWarn) -> bool;
    fn interface__msg__RadarWarn__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<RadarWarn>, size: usize) -> bool;
    fn interface__msg__RadarWarn__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<RadarWarn>);
    fn interface__msg__RadarWarn__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<RadarWarn>, out_seq: *mut rosidl_runtime_rs::Sequence<RadarWarn>) -> bool;
}

// Corresponds to interface__msg__RadarWarn
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct RadarWarn {

    // This member is not documented.
    #[allow(missing_docs)]
    pub header: std_msgs::msg::rmw::Header,

    /// 对应无人机 ID
    pub drone_id: u32,

    /// 世界坐标 X
    pub x: f64,

    /// 世界坐标 Y
    pub y: f64,

    /// 高度（米）
    pub z: f64,

    /// 置信度
    pub confidence: f64,

    /// 警告等级："LOW" / "MEDIUM" / "HIGH"
    pub warn_level: rosidl_runtime_rs::String,

    /// 报警描述（如 "Drone detected at zone A, height 50m"）
    pub description: rosidl_runtime_rs::String,

    /// 检测时间戳
    pub detected_at: builtin_interfaces::msg::rmw::Time,

}



impl Default for RadarWarn {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !interface__msg__RadarWarn__init(&mut msg as *mut _) {
        panic!("Call to interface__msg__RadarWarn__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for RadarWarn {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { interface__msg__RadarWarn__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { interface__msg__RadarWarn__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { interface__msg__RadarWarn__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for RadarWarn {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for RadarWarn where Self: Sized {
  const TYPE_NAME: &'static str = "interface/msg/RadarWarn";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__interface__msg__RadarWarn() }
  }
}


