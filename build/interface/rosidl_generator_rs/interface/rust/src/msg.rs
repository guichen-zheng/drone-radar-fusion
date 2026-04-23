#[cfg(feature = "serde")]
use serde::{Deserialize, Serialize};



// Corresponds to interface__msg__DroneDetect

// This struct is not documented.
#[allow(missing_docs)]

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct DroneDetect {

    // This member is not documented.
    #[allow(missing_docs)]
    pub header: std_msgs::msg::Header,

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
    pub label: std::string::String,

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
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::DroneDetect::default())
  }
}

impl rosidl_runtime_rs::Message for DroneDetect {
  type RmwMsg = super::msg::rmw::DroneDetect;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        header: std_msgs::msg::Header::into_rmw_message(std::borrow::Cow::Owned(msg.header)).into_owned(),
        drone_id: msg.drone_id,
        x: msg.x,
        y: msg.y,
        z: msg.z,
        vx: msg.vx,
        vy: msg.vy,
        vz: msg.vz,
        confidence: msg.confidence,
        bbox_x: msg.bbox_x,
        bbox_y: msg.bbox_y,
        bbox_w: msg.bbox_w,
        bbox_h: msg.bbox_h,
        label: msg.label.as_str().into(),
        is_tracked: msg.is_tracked,
        lat: msg.lat,
        lng: msg.lng,
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        header: std_msgs::msg::Header::into_rmw_message(std::borrow::Cow::Borrowed(&msg.header)).into_owned(),
      drone_id: msg.drone_id,
      x: msg.x,
      y: msg.y,
      z: msg.z,
      vx: msg.vx,
      vy: msg.vy,
      vz: msg.vz,
      confidence: msg.confidence,
      bbox_x: msg.bbox_x,
      bbox_y: msg.bbox_y,
      bbox_w: msg.bbox_w,
      bbox_h: msg.bbox_h,
        label: msg.label.as_str().into(),
      is_tracked: msg.is_tracked,
      lat: msg.lat,
      lng: msg.lng,
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      header: std_msgs::msg::Header::from_rmw_message(msg.header),
      drone_id: msg.drone_id,
      x: msg.x,
      y: msg.y,
      z: msg.z,
      vx: msg.vx,
      vy: msg.vy,
      vz: msg.vz,
      confidence: msg.confidence,
      bbox_x: msg.bbox_x,
      bbox_y: msg.bbox_y,
      bbox_w: msg.bbox_w,
      bbox_h: msg.bbox_h,
      label: msg.label.to_string(),
      is_tracked: msg.is_tracked,
      lat: msg.lat,
      lng: msg.lng,
    }
  }
}


// Corresponds to interface__msg__DroneDetectArray

// This struct is not documented.
#[allow(missing_docs)]

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct DroneDetectArray {

    // This member is not documented.
    #[allow(missing_docs)]
    pub header: std_msgs::msg::Header,

    /// 当前帧所有检测到的无人机列表
    pub drones: Vec<super::msg::DroneDetect>,

}



impl Default for DroneDetectArray {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::DroneDetectArray::default())
  }
}

impl rosidl_runtime_rs::Message for DroneDetectArray {
  type RmwMsg = super::msg::rmw::DroneDetectArray;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        header: std_msgs::msg::Header::into_rmw_message(std::borrow::Cow::Owned(msg.header)).into_owned(),
        drones: msg.drones
          .into_iter()
          .map(|elem| super::msg::DroneDetect::into_rmw_message(std::borrow::Cow::Owned(elem)).into_owned())
          .collect(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        header: std_msgs::msg::Header::into_rmw_message(std::borrow::Cow::Borrowed(&msg.header)).into_owned(),
        drones: msg.drones
          .iter()
          .map(|elem| super::msg::DroneDetect::into_rmw_message(std::borrow::Cow::Borrowed(elem)).into_owned())
          .collect(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      header: std_msgs::msg::Header::from_rmw_message(msg.header),
      drones: msg.drones
          .into_iter()
          .map(super::msg::DroneDetect::from_rmw_message)
          .collect(),
    }
  }
}


// Corresponds to interface__msg__RadarWarn

// This struct is not documented.
#[allow(missing_docs)]

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct RadarWarn {

    // This member is not documented.
    #[allow(missing_docs)]
    pub header: std_msgs::msg::Header,

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
    pub warn_level: std::string::String,

    /// 报警描述（如 "Drone detected at zone A, height 50m"）
    pub description: std::string::String,

    /// 检测时间戳
    pub detected_at: builtin_interfaces::msg::Time,

}



impl Default for RadarWarn {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::RadarWarn::default())
  }
}

impl rosidl_runtime_rs::Message for RadarWarn {
  type RmwMsg = super::msg::rmw::RadarWarn;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        header: std_msgs::msg::Header::into_rmw_message(std::borrow::Cow::Owned(msg.header)).into_owned(),
        drone_id: msg.drone_id,
        x: msg.x,
        y: msg.y,
        z: msg.z,
        confidence: msg.confidence,
        warn_level: msg.warn_level.as_str().into(),
        description: msg.description.as_str().into(),
        detected_at: builtin_interfaces::msg::Time::into_rmw_message(std::borrow::Cow::Owned(msg.detected_at)).into_owned(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        header: std_msgs::msg::Header::into_rmw_message(std::borrow::Cow::Borrowed(&msg.header)).into_owned(),
      drone_id: msg.drone_id,
      x: msg.x,
      y: msg.y,
      z: msg.z,
      confidence: msg.confidence,
        warn_level: msg.warn_level.as_str().into(),
        description: msg.description.as_str().into(),
        detected_at: builtin_interfaces::msg::Time::into_rmw_message(std::borrow::Cow::Borrowed(&msg.detected_at)).into_owned(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      header: std_msgs::msg::Header::from_rmw_message(msg.header),
      drone_id: msg.drone_id,
      x: msg.x,
      y: msg.y,
      z: msg.z,
      confidence: msg.confidence,
      warn_level: msg.warn_level.to_string(),
      description: msg.description.to_string(),
      detected_at: builtin_interfaces::msg::Time::from_rmw_message(msg.detected_at),
    }
  }
}


