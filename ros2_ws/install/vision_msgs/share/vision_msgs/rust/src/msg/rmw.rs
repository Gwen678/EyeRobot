#[cfg(feature = "serde")]
use serde::{Deserialize, Serialize};


#[link(name = "vision_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__vision_msgs__msg__BoundingBox2D() -> *const std::ffi::c_void;
}

#[link(name = "vision_msgs__rosidl_generator_c")]
extern "C" {
    fn vision_msgs__msg__BoundingBox2D__init(msg: *mut BoundingBox2D) -> bool;
    fn vision_msgs__msg__BoundingBox2D__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<BoundingBox2D>, size: usize) -> bool;
    fn vision_msgs__msg__BoundingBox2D__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<BoundingBox2D>);
    fn vision_msgs__msg__BoundingBox2D__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<BoundingBox2D>, out_seq: *mut rosidl_runtime_rs::Sequence<BoundingBox2D>) -> bool;
}

// Corresponds to vision_msgs__msg__BoundingBox2D
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]

/// A 2D bounding box that can be rotated about its center.
/// All dimensions are in pixels, but represented using floating-point
///   values to allow sub-pixel precision. If an exact pixel crop is required
///   for a rotated bounding box, it can be calculated using Bresenham's line
///   algorithm.

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct BoundingBox2D {
    /// The 2D position (in pixels) and orientation of the bounding box center.
    pub center: geometry_msgs::msg::rmw::Pose2D,

    /// The size (in pixels) of the bounding box surrounding the object relative
    ///   to the pose of its center.
    pub size_x: f64,


    // This member is not documented.
    #[allow(missing_docs)]
    pub size_y: f64,

}



impl Default for BoundingBox2D {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !vision_msgs__msg__BoundingBox2D__init(&mut msg as *mut _) {
        panic!("Call to vision_msgs__msg__BoundingBox2D__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for BoundingBox2D {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { vision_msgs__msg__BoundingBox2D__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { vision_msgs__msg__BoundingBox2D__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { vision_msgs__msg__BoundingBox2D__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for BoundingBox2D {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for BoundingBox2D where Self: Sized {
  const TYPE_NAME: &'static str = "vision_msgs/msg/BoundingBox2D";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__vision_msgs__msg__BoundingBox2D() }
  }
}


#[link(name = "vision_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__vision_msgs__msg__BoundingBox2DArray() -> *const std::ffi::c_void;
}

#[link(name = "vision_msgs__rosidl_generator_c")]
extern "C" {
    fn vision_msgs__msg__BoundingBox2DArray__init(msg: *mut BoundingBox2DArray) -> bool;
    fn vision_msgs__msg__BoundingBox2DArray__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<BoundingBox2DArray>, size: usize) -> bool;
    fn vision_msgs__msg__BoundingBox2DArray__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<BoundingBox2DArray>);
    fn vision_msgs__msg__BoundingBox2DArray__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<BoundingBox2DArray>, out_seq: *mut rosidl_runtime_rs::Sequence<BoundingBox2DArray>) -> bool;
}

// Corresponds to vision_msgs__msg__BoundingBox2DArray
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct BoundingBox2DArray {

    // This member is not documented.
    #[allow(missing_docs)]
    pub header: std_msgs::msg::rmw::Header,


    // This member is not documented.
    #[allow(missing_docs)]
    pub boxes: rosidl_runtime_rs::Sequence<super::super::msg::rmw::BoundingBox2D>,

}



impl Default for BoundingBox2DArray {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !vision_msgs__msg__BoundingBox2DArray__init(&mut msg as *mut _) {
        panic!("Call to vision_msgs__msg__BoundingBox2DArray__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for BoundingBox2DArray {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { vision_msgs__msg__BoundingBox2DArray__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { vision_msgs__msg__BoundingBox2DArray__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { vision_msgs__msg__BoundingBox2DArray__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for BoundingBox2DArray {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for BoundingBox2DArray where Self: Sized {
  const TYPE_NAME: &'static str = "vision_msgs/msg/BoundingBox2DArray";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__vision_msgs__msg__BoundingBox2DArray() }
  }
}


#[link(name = "vision_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__vision_msgs__msg__BoundingBox3D() -> *const std::ffi::c_void;
}

#[link(name = "vision_msgs__rosidl_generator_c")]
extern "C" {
    fn vision_msgs__msg__BoundingBox3D__init(msg: *mut BoundingBox3D) -> bool;
    fn vision_msgs__msg__BoundingBox3D__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<BoundingBox3D>, size: usize) -> bool;
    fn vision_msgs__msg__BoundingBox3D__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<BoundingBox3D>);
    fn vision_msgs__msg__BoundingBox3D__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<BoundingBox3D>, out_seq: *mut rosidl_runtime_rs::Sequence<BoundingBox3D>) -> bool;
}

// Corresponds to vision_msgs__msg__BoundingBox3D
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]

/// A 3D bounding box that can be positioned and rotated about its center (6 DOF)
/// Dimensions of this box are in meters, and as such, it may be migrated to
///   another package, such as geometry_msgs, in the future.

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct BoundingBox3D {
    /// The 3D position and orientation of the bounding box center
    pub center: geometry_msgs::msg::rmw::Pose,

    /// The size of the bounding box, in meters, surrounding the object's center
    ///   pose.
    pub size: geometry_msgs::msg::rmw::Vector3,

}



impl Default for BoundingBox3D {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !vision_msgs__msg__BoundingBox3D__init(&mut msg as *mut _) {
        panic!("Call to vision_msgs__msg__BoundingBox3D__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for BoundingBox3D {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { vision_msgs__msg__BoundingBox3D__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { vision_msgs__msg__BoundingBox3D__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { vision_msgs__msg__BoundingBox3D__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for BoundingBox3D {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for BoundingBox3D where Self: Sized {
  const TYPE_NAME: &'static str = "vision_msgs/msg/BoundingBox3D";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__vision_msgs__msg__BoundingBox3D() }
  }
}


#[link(name = "vision_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__vision_msgs__msg__BoundingBox3DArray() -> *const std::ffi::c_void;
}

#[link(name = "vision_msgs__rosidl_generator_c")]
extern "C" {
    fn vision_msgs__msg__BoundingBox3DArray__init(msg: *mut BoundingBox3DArray) -> bool;
    fn vision_msgs__msg__BoundingBox3DArray__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<BoundingBox3DArray>, size: usize) -> bool;
    fn vision_msgs__msg__BoundingBox3DArray__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<BoundingBox3DArray>);
    fn vision_msgs__msg__BoundingBox3DArray__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<BoundingBox3DArray>, out_seq: *mut rosidl_runtime_rs::Sequence<BoundingBox3DArray>) -> bool;
}

// Corresponds to vision_msgs__msg__BoundingBox3DArray
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct BoundingBox3DArray {

    // This member is not documented.
    #[allow(missing_docs)]
    pub header: std_msgs::msg::rmw::Header,


    // This member is not documented.
    #[allow(missing_docs)]
    pub boxes: rosidl_runtime_rs::Sequence<super::super::msg::rmw::BoundingBox3D>,

}



impl Default for BoundingBox3DArray {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !vision_msgs__msg__BoundingBox3DArray__init(&mut msg as *mut _) {
        panic!("Call to vision_msgs__msg__BoundingBox3DArray__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for BoundingBox3DArray {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { vision_msgs__msg__BoundingBox3DArray__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { vision_msgs__msg__BoundingBox3DArray__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { vision_msgs__msg__BoundingBox3DArray__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for BoundingBox3DArray {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for BoundingBox3DArray where Self: Sized {
  const TYPE_NAME: &'static str = "vision_msgs/msg/BoundingBox3DArray";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__vision_msgs__msg__BoundingBox3DArray() }
  }
}


#[link(name = "vision_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__vision_msgs__msg__Classification2D() -> *const std::ffi::c_void;
}

#[link(name = "vision_msgs__rosidl_generator_c")]
extern "C" {
    fn vision_msgs__msg__Classification2D__init(msg: *mut Classification2D) -> bool;
    fn vision_msgs__msg__Classification2D__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<Classification2D>, size: usize) -> bool;
    fn vision_msgs__msg__Classification2D__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<Classification2D>);
    fn vision_msgs__msg__Classification2D__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<Classification2D>, out_seq: *mut rosidl_runtime_rs::Sequence<Classification2D>) -> bool;
}

// Corresponds to vision_msgs__msg__Classification2D
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]

/// Defines a 2D classification result.
///
/// This result does not contain any position information. It is designed for
///   classifiers, which simply provide class probabilities given a source image.

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Classification2D {

    // This member is not documented.
    #[allow(missing_docs)]
    pub header: std_msgs::msg::rmw::Header,

    /// A list of class probabilities. This list need not provide a probability for
    ///   every possible class, just ones that are nonzero, or above some
    ///   user-defined threshold.
    pub results: rosidl_runtime_rs::Sequence<super::super::msg::rmw::ObjectHypothesis>,

    /// The 2D data that generated these results (i.e. region proposal cropped out of
    ///   the image). Not required for all use cases, so it may be empty.
    pub source_img: sensor_msgs::msg::rmw::Image,

}



impl Default for Classification2D {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !vision_msgs__msg__Classification2D__init(&mut msg as *mut _) {
        panic!("Call to vision_msgs__msg__Classification2D__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for Classification2D {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { vision_msgs__msg__Classification2D__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { vision_msgs__msg__Classification2D__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { vision_msgs__msg__Classification2D__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for Classification2D {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for Classification2D where Self: Sized {
  const TYPE_NAME: &'static str = "vision_msgs/msg/Classification2D";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__vision_msgs__msg__Classification2D() }
  }
}


#[link(name = "vision_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__vision_msgs__msg__Classification3D() -> *const std::ffi::c_void;
}

#[link(name = "vision_msgs__rosidl_generator_c")]
extern "C" {
    fn vision_msgs__msg__Classification3D__init(msg: *mut Classification3D) -> bool;
    fn vision_msgs__msg__Classification3D__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<Classification3D>, size: usize) -> bool;
    fn vision_msgs__msg__Classification3D__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<Classification3D>);
    fn vision_msgs__msg__Classification3D__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<Classification3D>, out_seq: *mut rosidl_runtime_rs::Sequence<Classification3D>) -> bool;
}

// Corresponds to vision_msgs__msg__Classification3D
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]

/// Defines a 3D classification result.
///
/// This result does not contain any position information. It is designed for
///   classifiers, which simply provide probabilities given a source image.

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Classification3D {

    // This member is not documented.
    #[allow(missing_docs)]
    pub header: std_msgs::msg::rmw::Header,

    /// Class probabilities
    pub results: rosidl_runtime_rs::Sequence<super::super::msg::rmw::ObjectHypothesis>,

    /// The 3D data that generated these results (i.e. region proposal cropped out of
    ///   the image). Not required for all detectors, so it may be empty.
    pub source_cloud: sensor_msgs::msg::rmw::PointCloud2,

}



impl Default for Classification3D {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !vision_msgs__msg__Classification3D__init(&mut msg as *mut _) {
        panic!("Call to vision_msgs__msg__Classification3D__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for Classification3D {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { vision_msgs__msg__Classification3D__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { vision_msgs__msg__Classification3D__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { vision_msgs__msg__Classification3D__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for Classification3D {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for Classification3D where Self: Sized {
  const TYPE_NAME: &'static str = "vision_msgs/msg/Classification3D";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__vision_msgs__msg__Classification3D() }
  }
}


#[link(name = "vision_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__vision_msgs__msg__Detection2DArray() -> *const std::ffi::c_void;
}

#[link(name = "vision_msgs__rosidl_generator_c")]
extern "C" {
    fn vision_msgs__msg__Detection2DArray__init(msg: *mut Detection2DArray) -> bool;
    fn vision_msgs__msg__Detection2DArray__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<Detection2DArray>, size: usize) -> bool;
    fn vision_msgs__msg__Detection2DArray__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<Detection2DArray>);
    fn vision_msgs__msg__Detection2DArray__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<Detection2DArray>, out_seq: *mut rosidl_runtime_rs::Sequence<Detection2DArray>) -> bool;
}

// Corresponds to vision_msgs__msg__Detection2DArray
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]

/// A list of 2D detections, for a multi-object 2D detector.

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Detection2DArray {

    // This member is not documented.
    #[allow(missing_docs)]
    pub header: std_msgs::msg::rmw::Header,

    /// A list of the detected proposals. A multi-proposal detector might generate
    ///   this list with many candidate detections generated from a single input.
    pub detections: rosidl_runtime_rs::Sequence<super::super::msg::rmw::Detection2D>,

}



impl Default for Detection2DArray {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !vision_msgs__msg__Detection2DArray__init(&mut msg as *mut _) {
        panic!("Call to vision_msgs__msg__Detection2DArray__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for Detection2DArray {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { vision_msgs__msg__Detection2DArray__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { vision_msgs__msg__Detection2DArray__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { vision_msgs__msg__Detection2DArray__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for Detection2DArray {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for Detection2DArray where Self: Sized {
  const TYPE_NAME: &'static str = "vision_msgs/msg/Detection2DArray";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__vision_msgs__msg__Detection2DArray() }
  }
}


#[link(name = "vision_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__vision_msgs__msg__Detection2D() -> *const std::ffi::c_void;
}

#[link(name = "vision_msgs__rosidl_generator_c")]
extern "C" {
    fn vision_msgs__msg__Detection2D__init(msg: *mut Detection2D) -> bool;
    fn vision_msgs__msg__Detection2D__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<Detection2D>, size: usize) -> bool;
    fn vision_msgs__msg__Detection2D__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<Detection2D>);
    fn vision_msgs__msg__Detection2D__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<Detection2D>, out_seq: *mut rosidl_runtime_rs::Sequence<Detection2D>) -> bool;
}

// Corresponds to vision_msgs__msg__Detection2D
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]

/// Defines a 2D detection result.
///
/// This is similar to a 2D classification, but includes position information,
///   allowing a classification result for a specific crop or image point to
///   to be located in the larger image.

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Detection2D {

    // This member is not documented.
    #[allow(missing_docs)]
    pub header: std_msgs::msg::rmw::Header,

    /// Class probabilities
    pub results: rosidl_runtime_rs::Sequence<super::super::msg::rmw::ObjectHypothesisWithPose>,

    /// 2D bounding box surrounding the object.
    pub bbox: super::super::msg::rmw::BoundingBox2D,

    /// The 2D data that generated these results (i.e. region proposal cropped out of
    ///   the image). Not required for all use cases, so it may be empty.
    pub source_img: sensor_msgs::msg::rmw::Image,

    /// If true, this message contains object tracking information.
    pub is_tracking: bool,

    /// ID used for consistency across multiple detection messages. This value will
    ///   likely differ from the id field set in each individual ObjectHypothesis.
    /// If you set this field, be sure to also set is_tracking to True.
    pub tracking_id: rosidl_runtime_rs::String,

}



impl Default for Detection2D {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !vision_msgs__msg__Detection2D__init(&mut msg as *mut _) {
        panic!("Call to vision_msgs__msg__Detection2D__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for Detection2D {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { vision_msgs__msg__Detection2D__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { vision_msgs__msg__Detection2D__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { vision_msgs__msg__Detection2D__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for Detection2D {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for Detection2D where Self: Sized {
  const TYPE_NAME: &'static str = "vision_msgs/msg/Detection2D";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__vision_msgs__msg__Detection2D() }
  }
}


#[link(name = "vision_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__vision_msgs__msg__Detection3DArray() -> *const std::ffi::c_void;
}

#[link(name = "vision_msgs__rosidl_generator_c")]
extern "C" {
    fn vision_msgs__msg__Detection3DArray__init(msg: *mut Detection3DArray) -> bool;
    fn vision_msgs__msg__Detection3DArray__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<Detection3DArray>, size: usize) -> bool;
    fn vision_msgs__msg__Detection3DArray__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<Detection3DArray>);
    fn vision_msgs__msg__Detection3DArray__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<Detection3DArray>, out_seq: *mut rosidl_runtime_rs::Sequence<Detection3DArray>) -> bool;
}

// Corresponds to vision_msgs__msg__Detection3DArray
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]

/// A list of 3D detections, for a multi-object 3D detector.

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Detection3DArray {

    // This member is not documented.
    #[allow(missing_docs)]
    pub header: std_msgs::msg::rmw::Header,

    /// A list of the detected proposals. A multi-proposal detector might generate
    ///   this list with many candidate detections generated from a single input.
    pub detections: rosidl_runtime_rs::Sequence<super::super::msg::rmw::Detection3D>,

}



impl Default for Detection3DArray {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !vision_msgs__msg__Detection3DArray__init(&mut msg as *mut _) {
        panic!("Call to vision_msgs__msg__Detection3DArray__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for Detection3DArray {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { vision_msgs__msg__Detection3DArray__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { vision_msgs__msg__Detection3DArray__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { vision_msgs__msg__Detection3DArray__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for Detection3DArray {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for Detection3DArray where Self: Sized {
  const TYPE_NAME: &'static str = "vision_msgs/msg/Detection3DArray";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__vision_msgs__msg__Detection3DArray() }
  }
}


#[link(name = "vision_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__vision_msgs__msg__Detection3D() -> *const std::ffi::c_void;
}

#[link(name = "vision_msgs__rosidl_generator_c")]
extern "C" {
    fn vision_msgs__msg__Detection3D__init(msg: *mut Detection3D) -> bool;
    fn vision_msgs__msg__Detection3D__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<Detection3D>, size: usize) -> bool;
    fn vision_msgs__msg__Detection3D__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<Detection3D>);
    fn vision_msgs__msg__Detection3D__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<Detection3D>, out_seq: *mut rosidl_runtime_rs::Sequence<Detection3D>) -> bool;
}

// Corresponds to vision_msgs__msg__Detection3D
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]

/// Defines a 3D detection result.
///
/// This extends a basic 3D classification by including position information,
///   allowing a classification result for a specific position in an image to
///   to be located in the larger image.

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Detection3D {

    // This member is not documented.
    #[allow(missing_docs)]
    pub header: std_msgs::msg::rmw::Header,

    /// Class probabilities. Does not have to include hypotheses for all possible
    ///   object ids, the scores for any ids not listed are assumed to be 0.
    pub results: rosidl_runtime_rs::Sequence<super::super::msg::rmw::ObjectHypothesisWithPose>,

    /// 3D bounding box surrounding the object.
    pub bbox: super::super::msg::rmw::BoundingBox3D,

    /// The 3D data that generated these results (i.e. region proposal cropped out of
    ///   the image). This information is not required for all detectors, so it may
    ///   be empty.
    pub source_cloud: sensor_msgs::msg::rmw::PointCloud2,

    /// If this message was tracking result, this field set true.
    pub is_tracking: bool,

    /// ID used for consistency across multiple detection messages. This value will
    ///   likely differ from the id field set in each individual ObjectHypothesis.
    /// If you set this field, be sure to also set is_tracking to True.
    pub tracking_id: rosidl_runtime_rs::String,

}



impl Default for Detection3D {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !vision_msgs__msg__Detection3D__init(&mut msg as *mut _) {
        panic!("Call to vision_msgs__msg__Detection3D__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for Detection3D {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { vision_msgs__msg__Detection3D__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { vision_msgs__msg__Detection3D__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { vision_msgs__msg__Detection3D__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for Detection3D {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for Detection3D where Self: Sized {
  const TYPE_NAME: &'static str = "vision_msgs/msg/Detection3D";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__vision_msgs__msg__Detection3D() }
  }
}


#[link(name = "vision_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__vision_msgs__msg__ObjectHypothesis() -> *const std::ffi::c_void;
}

#[link(name = "vision_msgs__rosidl_generator_c")]
extern "C" {
    fn vision_msgs__msg__ObjectHypothesis__init(msg: *mut ObjectHypothesis) -> bool;
    fn vision_msgs__msg__ObjectHypothesis__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<ObjectHypothesis>, size: usize) -> bool;
    fn vision_msgs__msg__ObjectHypothesis__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<ObjectHypothesis>);
    fn vision_msgs__msg__ObjectHypothesis__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<ObjectHypothesis>, out_seq: *mut rosidl_runtime_rs::Sequence<ObjectHypothesis>) -> bool;
}

// Corresponds to vision_msgs__msg__ObjectHypothesis
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]

/// An object hypothesis that contains no position information.

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct ObjectHypothesis {
    /// The unique ID of the object class. To get additional information about
    ///   this ID, such as its human-readable class name, listeners should perform a
    ///   lookup in a metadata database. See vision_msgs/VisionInfo.msg for more detail.
    pub id: rosidl_runtime_rs::String,

    /// The probability or confidence value of the detected object. By convention,
    ///   this value should lie in the range.
    pub score: f64,

}



impl Default for ObjectHypothesis {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !vision_msgs__msg__ObjectHypothesis__init(&mut msg as *mut _) {
        panic!("Call to vision_msgs__msg__ObjectHypothesis__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for ObjectHypothesis {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { vision_msgs__msg__ObjectHypothesis__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { vision_msgs__msg__ObjectHypothesis__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { vision_msgs__msg__ObjectHypothesis__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for ObjectHypothesis {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for ObjectHypothesis where Self: Sized {
  const TYPE_NAME: &'static str = "vision_msgs/msg/ObjectHypothesis";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__vision_msgs__msg__ObjectHypothesis() }
  }
}


#[link(name = "vision_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__vision_msgs__msg__ObjectHypothesisWithPose() -> *const std::ffi::c_void;
}

#[link(name = "vision_msgs__rosidl_generator_c")]
extern "C" {
    fn vision_msgs__msg__ObjectHypothesisWithPose__init(msg: *mut ObjectHypothesisWithPose) -> bool;
    fn vision_msgs__msg__ObjectHypothesisWithPose__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<ObjectHypothesisWithPose>, size: usize) -> bool;
    fn vision_msgs__msg__ObjectHypothesisWithPose__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<ObjectHypothesisWithPose>);
    fn vision_msgs__msg__ObjectHypothesisWithPose__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<ObjectHypothesisWithPose>, out_seq: *mut rosidl_runtime_rs::Sequence<ObjectHypothesisWithPose>) -> bool;
}

// Corresponds to vision_msgs__msg__ObjectHypothesisWithPose
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]

/// An object hypothesis that contains position information.

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct ObjectHypothesisWithPose {
    /// The unique ID of the object class. To get additional information about
    ///   this ID, such as its human-readable class name, listeners should perform a
    ///   lookup in a metadata database. See vision_msgs/VisionInfo.msg for more detail.
    pub id: rosidl_runtime_rs::String,

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
    pub pose: geometry_msgs::msg::rmw::PoseWithCovariance,

}



impl Default for ObjectHypothesisWithPose {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !vision_msgs__msg__ObjectHypothesisWithPose__init(&mut msg as *mut _) {
        panic!("Call to vision_msgs__msg__ObjectHypothesisWithPose__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for ObjectHypothesisWithPose {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { vision_msgs__msg__ObjectHypothesisWithPose__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { vision_msgs__msg__ObjectHypothesisWithPose__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { vision_msgs__msg__ObjectHypothesisWithPose__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for ObjectHypothesisWithPose {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for ObjectHypothesisWithPose where Self: Sized {
  const TYPE_NAME: &'static str = "vision_msgs/msg/ObjectHypothesisWithPose";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__vision_msgs__msg__ObjectHypothesisWithPose() }
  }
}


#[link(name = "vision_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__vision_msgs__msg__VisionInfo() -> *const std::ffi::c_void;
}

#[link(name = "vision_msgs__rosidl_generator_c")]
extern "C" {
    fn vision_msgs__msg__VisionInfo__init(msg: *mut VisionInfo) -> bool;
    fn vision_msgs__msg__VisionInfo__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<VisionInfo>, size: usize) -> bool;
    fn vision_msgs__msg__VisionInfo__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<VisionInfo>);
    fn vision_msgs__msg__VisionInfo__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<VisionInfo>, out_seq: *mut rosidl_runtime_rs::Sequence<VisionInfo>) -> bool;
}

// Corresponds to vision_msgs__msg__VisionInfo
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]

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

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct VisionInfo {
    /// Used for sequencing
    pub header: std_msgs::msg::rmw::Header,

    /// Name of the vision pipeline. This should be a value that is meaningful to an
    ///   outside user.
    pub method: rosidl_runtime_rs::String,

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
    pub database_location: rosidl_runtime_rs::String,

    /// Metadata database version. This counter is incremented
    ///   each time the pipeline begins using a new version of the database (useful
    ///   in the case of online training or user modifications).
    ///   The counter value can be monitored by listeners to ensure that the pipeline
    ///   and the listener are using the same metadata.
    pub database_version: i32,

}



impl Default for VisionInfo {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !vision_msgs__msg__VisionInfo__init(&mut msg as *mut _) {
        panic!("Call to vision_msgs__msg__VisionInfo__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for VisionInfo {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { vision_msgs__msg__VisionInfo__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { vision_msgs__msg__VisionInfo__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { vision_msgs__msg__VisionInfo__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for VisionInfo {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for VisionInfo where Self: Sized {
  const TYPE_NAME: &'static str = "vision_msgs/msg/VisionInfo";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__vision_msgs__msg__VisionInfo() }
  }
}


