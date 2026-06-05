#[cfg(feature = "serde")]
use serde::{Deserialize, Serialize};



// Corresponds to vision_msgs__msg__BoundingBox2D
/// A 2D bounding box that can be rotated about its center.
/// All dimensions are in pixels, but represented using floating-point
///   values to allow sub-pixel precision. If an exact pixel crop is required
///   for a rotated bounding box, it can be calculated using Bresenham's line
///   algorithm.

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct BoundingBox2D {
    /// The 2D position (in pixels) and orientation of the bounding box center.
    pub center: geometry_msgs::msg::Pose2D,

    /// The size (in pixels) of the bounding box surrounding the object relative
    ///   to the pose of its center.
    pub size_x: f64,


    // This member is not documented.
    #[allow(missing_docs)]
    pub size_y: f64,

}



impl Default for BoundingBox2D {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::BoundingBox2D::default())
  }
}

impl rosidl_runtime_rs::Message for BoundingBox2D {
  type RmwMsg = super::msg::rmw::BoundingBox2D;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        center: geometry_msgs::msg::Pose2D::into_rmw_message(std::borrow::Cow::Owned(msg.center)).into_owned(),
        size_x: msg.size_x,
        size_y: msg.size_y,
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        center: geometry_msgs::msg::Pose2D::into_rmw_message(std::borrow::Cow::Borrowed(&msg.center)).into_owned(),
      size_x: msg.size_x,
      size_y: msg.size_y,
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      center: geometry_msgs::msg::Pose2D::from_rmw_message(msg.center),
      size_x: msg.size_x,
      size_y: msg.size_y,
    }
  }
}


// Corresponds to vision_msgs__msg__BoundingBox2DArray

// This struct is not documented.
#[allow(missing_docs)]

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct BoundingBox2DArray {

    // This member is not documented.
    #[allow(missing_docs)]
    pub header: std_msgs::msg::Header,


    // This member is not documented.
    #[allow(missing_docs)]
    pub boxes: Vec<super::msg::BoundingBox2D>,

}



impl Default for BoundingBox2DArray {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::BoundingBox2DArray::default())
  }
}

impl rosidl_runtime_rs::Message for BoundingBox2DArray {
  type RmwMsg = super::msg::rmw::BoundingBox2DArray;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        header: std_msgs::msg::Header::into_rmw_message(std::borrow::Cow::Owned(msg.header)).into_owned(),
        boxes: msg.boxes
          .into_iter()
          .map(|elem| super::msg::BoundingBox2D::into_rmw_message(std::borrow::Cow::Owned(elem)).into_owned())
          .collect(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        header: std_msgs::msg::Header::into_rmw_message(std::borrow::Cow::Borrowed(&msg.header)).into_owned(),
        boxes: msg.boxes
          .iter()
          .map(|elem| super::msg::BoundingBox2D::into_rmw_message(std::borrow::Cow::Borrowed(elem)).into_owned())
          .collect(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      header: std_msgs::msg::Header::from_rmw_message(msg.header),
      boxes: msg.boxes
          .into_iter()
          .map(super::msg::BoundingBox2D::from_rmw_message)
          .collect(),
    }
  }
}


// Corresponds to vision_msgs__msg__BoundingBox3D
/// A 3D bounding box that can be positioned and rotated about its center (6 DOF)
/// Dimensions of this box are in meters, and as such, it may be migrated to
///   another package, such as geometry_msgs, in the future.

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct BoundingBox3D {
    /// The 3D position and orientation of the bounding box center
    pub center: geometry_msgs::msg::Pose,

    /// The size of the bounding box, in meters, surrounding the object's center
    ///   pose.
    pub size: geometry_msgs::msg::Vector3,

}



impl Default for BoundingBox3D {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::BoundingBox3D::default())
  }
}

impl rosidl_runtime_rs::Message for BoundingBox3D {
  type RmwMsg = super::msg::rmw::BoundingBox3D;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        center: geometry_msgs::msg::Pose::into_rmw_message(std::borrow::Cow::Owned(msg.center)).into_owned(),
        size: geometry_msgs::msg::Vector3::into_rmw_message(std::borrow::Cow::Owned(msg.size)).into_owned(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        center: geometry_msgs::msg::Pose::into_rmw_message(std::borrow::Cow::Borrowed(&msg.center)).into_owned(),
        size: geometry_msgs::msg::Vector3::into_rmw_message(std::borrow::Cow::Borrowed(&msg.size)).into_owned(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      center: geometry_msgs::msg::Pose::from_rmw_message(msg.center),
      size: geometry_msgs::msg::Vector3::from_rmw_message(msg.size),
    }
  }
}


// Corresponds to vision_msgs__msg__BoundingBox3DArray

// This struct is not documented.
#[allow(missing_docs)]

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct BoundingBox3DArray {

    // This member is not documented.
    #[allow(missing_docs)]
    pub header: std_msgs::msg::Header,


    // This member is not documented.
    #[allow(missing_docs)]
    pub boxes: Vec<super::msg::BoundingBox3D>,

}



impl Default for BoundingBox3DArray {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::BoundingBox3DArray::default())
  }
}

impl rosidl_runtime_rs::Message for BoundingBox3DArray {
  type RmwMsg = super::msg::rmw::BoundingBox3DArray;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        header: std_msgs::msg::Header::into_rmw_message(std::borrow::Cow::Owned(msg.header)).into_owned(),
        boxes: msg.boxes
          .into_iter()
          .map(|elem| super::msg::BoundingBox3D::into_rmw_message(std::borrow::Cow::Owned(elem)).into_owned())
          .collect(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        header: std_msgs::msg::Header::into_rmw_message(std::borrow::Cow::Borrowed(&msg.header)).into_owned(),
        boxes: msg.boxes
          .iter()
          .map(|elem| super::msg::BoundingBox3D::into_rmw_message(std::borrow::Cow::Borrowed(elem)).into_owned())
          .collect(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      header: std_msgs::msg::Header::from_rmw_message(msg.header),
      boxes: msg.boxes
          .into_iter()
          .map(super::msg::BoundingBox3D::from_rmw_message)
          .collect(),
    }
  }
}


// Corresponds to vision_msgs__msg__Classification2D
/// Defines a 2D classification result.
///
/// This result does not contain any position information. It is designed for
///   classifiers, which simply provide class probabilities given a source image.

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Classification2D {

    // This member is not documented.
    #[allow(missing_docs)]
    pub header: std_msgs::msg::Header,

    /// A list of class probabilities. This list need not provide a probability for
    ///   every possible class, just ones that are nonzero, or above some
    ///   user-defined threshold.
    pub results: Vec<super::msg::ObjectHypothesis>,

    /// The 2D data that generated these results (i.e. region proposal cropped out of
    ///   the image). Not required for all use cases, so it may be empty.
    pub source_img: sensor_msgs::msg::Image,

}



impl Default for Classification2D {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::Classification2D::default())
  }
}

impl rosidl_runtime_rs::Message for Classification2D {
  type RmwMsg = super::msg::rmw::Classification2D;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        header: std_msgs::msg::Header::into_rmw_message(std::borrow::Cow::Owned(msg.header)).into_owned(),
        results: msg.results
          .into_iter()
          .map(|elem| super::msg::ObjectHypothesis::into_rmw_message(std::borrow::Cow::Owned(elem)).into_owned())
          .collect(),
        source_img: sensor_msgs::msg::Image::into_rmw_message(std::borrow::Cow::Owned(msg.source_img)).into_owned(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        header: std_msgs::msg::Header::into_rmw_message(std::borrow::Cow::Borrowed(&msg.header)).into_owned(),
        results: msg.results
          .iter()
          .map(|elem| super::msg::ObjectHypothesis::into_rmw_message(std::borrow::Cow::Borrowed(elem)).into_owned())
          .collect(),
        source_img: sensor_msgs::msg::Image::into_rmw_message(std::borrow::Cow::Borrowed(&msg.source_img)).into_owned(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      header: std_msgs::msg::Header::from_rmw_message(msg.header),
      results: msg.results
          .into_iter()
          .map(super::msg::ObjectHypothesis::from_rmw_message)
          .collect(),
      source_img: sensor_msgs::msg::Image::from_rmw_message(msg.source_img),
    }
  }
}


// Corresponds to vision_msgs__msg__Classification3D
/// Defines a 3D classification result.
///
/// This result does not contain any position information. It is designed for
///   classifiers, which simply provide probabilities given a source image.

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Classification3D {

    // This member is not documented.
    #[allow(missing_docs)]
    pub header: std_msgs::msg::Header,

    /// Class probabilities
    pub results: Vec<super::msg::ObjectHypothesis>,

    /// The 3D data that generated these results (i.e. region proposal cropped out of
    ///   the image). Not required for all detectors, so it may be empty.
    pub source_cloud: sensor_msgs::msg::PointCloud2,

}



impl Default for Classification3D {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::Classification3D::default())
  }
}

impl rosidl_runtime_rs::Message for Classification3D {
  type RmwMsg = super::msg::rmw::Classification3D;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        header: std_msgs::msg::Header::into_rmw_message(std::borrow::Cow::Owned(msg.header)).into_owned(),
        results: msg.results
          .into_iter()
          .map(|elem| super::msg::ObjectHypothesis::into_rmw_message(std::borrow::Cow::Owned(elem)).into_owned())
          .collect(),
        source_cloud: sensor_msgs::msg::PointCloud2::into_rmw_message(std::borrow::Cow::Owned(msg.source_cloud)).into_owned(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        header: std_msgs::msg::Header::into_rmw_message(std::borrow::Cow::Borrowed(&msg.header)).into_owned(),
        results: msg.results
          .iter()
          .map(|elem| super::msg::ObjectHypothesis::into_rmw_message(std::borrow::Cow::Borrowed(elem)).into_owned())
          .collect(),
        source_cloud: sensor_msgs::msg::PointCloud2::into_rmw_message(std::borrow::Cow::Borrowed(&msg.source_cloud)).into_owned(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      header: std_msgs::msg::Header::from_rmw_message(msg.header),
      results: msg.results
          .into_iter()
          .map(super::msg::ObjectHypothesis::from_rmw_message)
          .collect(),
      source_cloud: sensor_msgs::msg::PointCloud2::from_rmw_message(msg.source_cloud),
    }
  }
}


// Corresponds to vision_msgs__msg__Detection2DArray
/// A list of 2D detections, for a multi-object 2D detector.

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Detection2DArray {

    // This member is not documented.
    #[allow(missing_docs)]
    pub header: std_msgs::msg::Header,

    /// A list of the detected proposals. A multi-proposal detector might generate
    ///   this list with many candidate detections generated from a single input.
    pub detections: Vec<super::msg::Detection2D>,

}



impl Default for Detection2DArray {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::Detection2DArray::default())
  }
}

impl rosidl_runtime_rs::Message for Detection2DArray {
  type RmwMsg = super::msg::rmw::Detection2DArray;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        header: std_msgs::msg::Header::into_rmw_message(std::borrow::Cow::Owned(msg.header)).into_owned(),
        detections: msg.detections
          .into_iter()
          .map(|elem| super::msg::Detection2D::into_rmw_message(std::borrow::Cow::Owned(elem)).into_owned())
          .collect(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        header: std_msgs::msg::Header::into_rmw_message(std::borrow::Cow::Borrowed(&msg.header)).into_owned(),
        detections: msg.detections
          .iter()
          .map(|elem| super::msg::Detection2D::into_rmw_message(std::borrow::Cow::Borrowed(elem)).into_owned())
          .collect(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      header: std_msgs::msg::Header::from_rmw_message(msg.header),
      detections: msg.detections
          .into_iter()
          .map(super::msg::Detection2D::from_rmw_message)
          .collect(),
    }
  }
}


// Corresponds to vision_msgs__msg__Detection2D
/// Defines a 2D detection result.
///
/// This is similar to a 2D classification, but includes position information,
///   allowing a classification result for a specific crop or image point to
///   to be located in the larger image.

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Detection2D {

    // This member is not documented.
    #[allow(missing_docs)]
    pub header: std_msgs::msg::Header,

    /// Class probabilities
    pub results: Vec<super::msg::ObjectHypothesisWithPose>,

    /// 2D bounding box surrounding the object.
    pub bbox: super::msg::BoundingBox2D,

    /// The 2D data that generated these results (i.e. region proposal cropped out of
    ///   the image). Not required for all use cases, so it may be empty.
    pub source_img: sensor_msgs::msg::Image,

    /// If true, this message contains object tracking information.
    pub is_tracking: bool,

    /// ID used for consistency across multiple detection messages. This value will
    ///   likely differ from the id field set in each individual ObjectHypothesis.
    /// If you set this field, be sure to also set is_tracking to True.
    pub tracking_id: std::string::String,

}



impl Default for Detection2D {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::Detection2D::default())
  }
}

impl rosidl_runtime_rs::Message for Detection2D {
  type RmwMsg = super::msg::rmw::Detection2D;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        header: std_msgs::msg::Header::into_rmw_message(std::borrow::Cow::Owned(msg.header)).into_owned(),
        results: msg.results
          .into_iter()
          .map(|elem| super::msg::ObjectHypothesisWithPose::into_rmw_message(std::borrow::Cow::Owned(elem)).into_owned())
          .collect(),
        bbox: super::msg::BoundingBox2D::into_rmw_message(std::borrow::Cow::Owned(msg.bbox)).into_owned(),
        source_img: sensor_msgs::msg::Image::into_rmw_message(std::borrow::Cow::Owned(msg.source_img)).into_owned(),
        is_tracking: msg.is_tracking,
        tracking_id: msg.tracking_id.as_str().into(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        header: std_msgs::msg::Header::into_rmw_message(std::borrow::Cow::Borrowed(&msg.header)).into_owned(),
        results: msg.results
          .iter()
          .map(|elem| super::msg::ObjectHypothesisWithPose::into_rmw_message(std::borrow::Cow::Borrowed(elem)).into_owned())
          .collect(),
        bbox: super::msg::BoundingBox2D::into_rmw_message(std::borrow::Cow::Borrowed(&msg.bbox)).into_owned(),
        source_img: sensor_msgs::msg::Image::into_rmw_message(std::borrow::Cow::Borrowed(&msg.source_img)).into_owned(),
      is_tracking: msg.is_tracking,
        tracking_id: msg.tracking_id.as_str().into(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      header: std_msgs::msg::Header::from_rmw_message(msg.header),
      results: msg.results
          .into_iter()
          .map(super::msg::ObjectHypothesisWithPose::from_rmw_message)
          .collect(),
      bbox: super::msg::BoundingBox2D::from_rmw_message(msg.bbox),
      source_img: sensor_msgs::msg::Image::from_rmw_message(msg.source_img),
      is_tracking: msg.is_tracking,
      tracking_id: msg.tracking_id.to_string(),
    }
  }
}


// Corresponds to vision_msgs__msg__Detection3DArray
/// A list of 3D detections, for a multi-object 3D detector.

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Detection3DArray {

    // This member is not documented.
    #[allow(missing_docs)]
    pub header: std_msgs::msg::Header,

    /// A list of the detected proposals. A multi-proposal detector might generate
    ///   this list with many candidate detections generated from a single input.
    pub detections: Vec<super::msg::Detection3D>,

}



impl Default for Detection3DArray {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::Detection3DArray::default())
  }
}

impl rosidl_runtime_rs::Message for Detection3DArray {
  type RmwMsg = super::msg::rmw::Detection3DArray;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        header: std_msgs::msg::Header::into_rmw_message(std::borrow::Cow::Owned(msg.header)).into_owned(),
        detections: msg.detections
          .into_iter()
          .map(|elem| super::msg::Detection3D::into_rmw_message(std::borrow::Cow::Owned(elem)).into_owned())
          .collect(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        header: std_msgs::msg::Header::into_rmw_message(std::borrow::Cow::Borrowed(&msg.header)).into_owned(),
        detections: msg.detections
          .iter()
          .map(|elem| super::msg::Detection3D::into_rmw_message(std::borrow::Cow::Borrowed(elem)).into_owned())
          .collect(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      header: std_msgs::msg::Header::from_rmw_message(msg.header),
      detections: msg.detections
          .into_iter()
          .map(super::msg::Detection3D::from_rmw_message)
          .collect(),
    }
  }
}


// Corresponds to vision_msgs__msg__Detection3D
/// Defines a 3D detection result.
///
/// This extends a basic 3D classification by including position information,
///   allowing a classification result for a specific position in an image to
///   to be located in the larger image.

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Detection3D {

    // This member is not documented.
    #[allow(missing_docs)]
    pub header: std_msgs::msg::Header,

    /// Class probabilities. Does not have to include hypotheses for all possible
    ///   object ids, the scores for any ids not listed are assumed to be 0.
    pub results: Vec<super::msg::ObjectHypothesisWithPose>,

    /// 3D bounding box surrounding the object.
    pub bbox: super::msg::BoundingBox3D,

    /// The 3D data that generated these results (i.e. region proposal cropped out of
    ///   the image). This information is not required for all detectors, so it may
    ///   be empty.
    pub source_cloud: sensor_msgs::msg::PointCloud2,

    /// If this message was tracking result, this field set true.
    pub is_tracking: bool,

    /// ID used for consistency across multiple detection messages. This value will
    ///   likely differ from the id field set in each individual ObjectHypothesis.
    /// If you set this field, be sure to also set is_tracking to True.
    pub tracking_id: std::string::String,

}



impl Default for Detection3D {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::Detection3D::default())
  }
}

impl rosidl_runtime_rs::Message for Detection3D {
  type RmwMsg = super::msg::rmw::Detection3D;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        header: std_msgs::msg::Header::into_rmw_message(std::borrow::Cow::Owned(msg.header)).into_owned(),
        results: msg.results
          .into_iter()
          .map(|elem| super::msg::ObjectHypothesisWithPose::into_rmw_message(std::borrow::Cow::Owned(elem)).into_owned())
          .collect(),
        bbox: super::msg::BoundingBox3D::into_rmw_message(std::borrow::Cow::Owned(msg.bbox)).into_owned(),
        source_cloud: sensor_msgs::msg::PointCloud2::into_rmw_message(std::borrow::Cow::Owned(msg.source_cloud)).into_owned(),
        is_tracking: msg.is_tracking,
        tracking_id: msg.tracking_id.as_str().into(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        header: std_msgs::msg::Header::into_rmw_message(std::borrow::Cow::Borrowed(&msg.header)).into_owned(),
        results: msg.results
          .iter()
          .map(|elem| super::msg::ObjectHypothesisWithPose::into_rmw_message(std::borrow::Cow::Borrowed(elem)).into_owned())
          .collect(),
        bbox: super::msg::BoundingBox3D::into_rmw_message(std::borrow::Cow::Borrowed(&msg.bbox)).into_owned(),
        source_cloud: sensor_msgs::msg::PointCloud2::into_rmw_message(std::borrow::Cow::Borrowed(&msg.source_cloud)).into_owned(),
      is_tracking: msg.is_tracking,
        tracking_id: msg.tracking_id.as_str().into(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      header: std_msgs::msg::Header::from_rmw_message(msg.header),
      results: msg.results
          .into_iter()
          .map(super::msg::ObjectHypothesisWithPose::from_rmw_message)
          .collect(),
      bbox: super::msg::BoundingBox3D::from_rmw_message(msg.bbox),
      source_cloud: sensor_msgs::msg::PointCloud2::from_rmw_message(msg.source_cloud),
      is_tracking: msg.is_tracking,
      tracking_id: msg.tracking_id.to_string(),
    }
  }
}


// Corresponds to vision_msgs__msg__ObjectHypothesis
/// An object hypothesis that contains no position information.

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct ObjectHypothesis {
    /// The unique ID of the object class. To get additional information about
    ///   this ID, such as its human-readable class name, listeners should perform a
    ///   lookup in a metadata database. See vision_msgs/VisionInfo.msg for more detail.
    pub id: std::string::String,

    /// The probability or confidence value of the detected object. By convention,
    ///   this value should lie in the range.
    pub score: f64,

}



impl Default for ObjectHypothesis {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::ObjectHypothesis::default())
  }
}

impl rosidl_runtime_rs::Message for ObjectHypothesis {
  type RmwMsg = super::msg::rmw::ObjectHypothesis;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        id: msg.id.as_str().into(),
        score: msg.score,
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        id: msg.id.as_str().into(),
      score: msg.score,
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      id: msg.id.to_string(),
      score: msg.score,
    }
  }
}


// Corresponds to vision_msgs__msg__ObjectHypothesisWithPose
/// An object hypothesis that contains position information.

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct ObjectHypothesisWithPose {
    /// The unique ID of the object class. To get additional information about
    ///   this ID, such as its human-readable class name, listeners should perform a
    ///   lookup in a metadata database. See vision_msgs/VisionInfo.msg for more detail.
    pub id: std::string::String,

    /// The probability or confidence value of the detected object. By convention,
    ///   this value should lie in the range.
    pub score: f64,

    /// The 6D pose of the object hypothesis. This pose should be
    ///   defined as the pose of some fixed reference point on the object, such a
    ///   the geometric center of the bounding box or the center of mass of the
    ///   object.
    /// Note that this pose is not stamped; frame information can be defined by
    ///   parent messages.
    /// Also note that different classes predicted for the same input data may have
    ///   different predicted 6D poses.
    pub pose: geometry_msgs::msg::PoseWithCovariance,

}



impl Default for ObjectHypothesisWithPose {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::ObjectHypothesisWithPose::default())
  }
}

impl rosidl_runtime_rs::Message for ObjectHypothesisWithPose {
  type RmwMsg = super::msg::rmw::ObjectHypothesisWithPose;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        id: msg.id.as_str().into(),
        score: msg.score,
        pose: geometry_msgs::msg::PoseWithCovariance::into_rmw_message(std::borrow::Cow::Owned(msg.pose)).into_owned(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        id: msg.id.as_str().into(),
      score: msg.score,
        pose: geometry_msgs::msg::PoseWithCovariance::into_rmw_message(std::borrow::Cow::Borrowed(&msg.pose)).into_owned(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      id: msg.id.to_string(),
      score: msg.score,
      pose: geometry_msgs::msg::PoseWithCovariance::from_rmw_message(msg.pose),
    }
  }
}


// Corresponds to vision_msgs__msg__VisionInfo
/// Provides meta-information about a visual pipeline.
///
/// This message serves a similar purpose to sensor_msgs/CameraInfo, but instead
///   of being tied to hardware, it represents information about a specific
///   computer vision pipeline. This information stays constant (or relatively
///   constant) over time, and so it is wasteful to send it with each individual
///   result. By listening to these messages, subscribers will receive
///   the context in which published vision messages are to be interpreted.
/// Each vision pipeline should publish its VisionInfo messages to its own topic,
///   in a manner similar to CameraInfo.

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct VisionInfo {
    /// Used for sequencing
    pub header: std_msgs::msg::Header,

    /// Name of the vision pipeline. This should be a value that is meaningful to an
    ///   outside user.
    pub method: std::string::String,

    /// Location where the metadata database is stored. The recommended location is
    ///   as an XML string on the ROS parameter server, but the exact implementation
    ///   and information is left up to the user.
    /// The database should store information attached to class ids. Each
    ///   class id should map to an atomic, visually recognizable element. This
    ///   definition is intentionally vague to allow extreme flexibility. The
    ///   elements could be classes in a pixel segmentation algorithm, object classes
    ///   in a detector, different people's faces in a face detection algorithm, etc.
    ///   Vision pipelines report results in terms of numeric IDs, which map into
    ///   this  database.
    /// The information stored in this database is, again, left up to the user. The
    ///   database could be as simple as a map from ID to class name, or it could
    ///   include information such as object meshes or colors to use for
    ///   visualization.
    pub database_location: std::string::String,

    /// Metadata database version. This counter is incremented
    ///   each time the pipeline begins using a new version of the database (useful
    ///   in the case of online training or user modifications).
    ///   The counter value can be monitored by listeners to ensure that the pipeline
    ///   and the listener are using the same metadata.
    pub database_version: i32,

}



impl Default for VisionInfo {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::VisionInfo::default())
  }
}

impl rosidl_runtime_rs::Message for VisionInfo {
  type RmwMsg = super::msg::rmw::VisionInfo;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        header: std_msgs::msg::Header::into_rmw_message(std::borrow::Cow::Owned(msg.header)).into_owned(),
        method: msg.method.as_str().into(),
        database_location: msg.database_location.as_str().into(),
        database_version: msg.database_version,
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        header: std_msgs::msg::Header::into_rmw_message(std::borrow::Cow::Borrowed(&msg.header)).into_owned(),
        method: msg.method.as_str().into(),
        database_location: msg.database_location.as_str().into(),
      database_version: msg.database_version,
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      header: std_msgs::msg::Header::from_rmw_message(msg.header),
      method: msg.method.to_string(),
      database_location: msg.database_location.to_string(),
      database_version: msg.database_version,
    }
  }
}


