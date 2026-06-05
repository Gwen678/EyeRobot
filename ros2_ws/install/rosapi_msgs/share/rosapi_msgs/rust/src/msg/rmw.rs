#[cfg(feature = "serde")]
use serde::{Deserialize, Serialize};


#[link(name = "rosapi_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__rosapi_msgs__msg__TypeDef() -> *const std::ffi::c_void;
}

#[link(name = "rosapi_msgs__rosidl_generator_c")]
extern "C" {
    fn rosapi_msgs__msg__TypeDef__init(msg: *mut TypeDef) -> bool;
    fn rosapi_msgs__msg__TypeDef__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<TypeDef>, size: usize) -> bool;
    fn rosapi_msgs__msg__TypeDef__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<TypeDef>);
    fn rosapi_msgs__msg__TypeDef__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<TypeDef>, out_seq: *mut rosidl_runtime_rs::Sequence<TypeDef>) -> bool;
}

// Corresponds to rosapi_msgs__msg__TypeDef
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct TypeDef {

    // This member is not documented.
    #[allow(missing_docs)]
    pub type_: rosidl_runtime_rs::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub fieldnames: rosidl_runtime_rs::Sequence<rosidl_runtime_rs::String>,


    // This member is not documented.
    #[allow(missing_docs)]
    pub fieldtypes: rosidl_runtime_rs::Sequence<rosidl_runtime_rs::String>,


    // This member is not documented.
    #[allow(missing_docs)]
    pub fieldarraylen: rosidl_runtime_rs::Sequence<i32>,


    // This member is not documented.
    #[allow(missing_docs)]
    pub examples: rosidl_runtime_rs::Sequence<rosidl_runtime_rs::String>,


    // This member is not documented.
    #[allow(missing_docs)]
    pub constnames: rosidl_runtime_rs::Sequence<rosidl_runtime_rs::String>,


    // This member is not documented.
    #[allow(missing_docs)]
    pub constvalues: rosidl_runtime_rs::Sequence<rosidl_runtime_rs::String>,

}



impl Default for TypeDef {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !rosapi_msgs__msg__TypeDef__init(&mut msg as *mut _) {
        panic!("Call to rosapi_msgs__msg__TypeDef__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for TypeDef {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__msg__TypeDef__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__msg__TypeDef__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__msg__TypeDef__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for TypeDef {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for TypeDef where Self: Sized {
  const TYPE_NAME: &'static str = "rosapi_msgs/msg/TypeDef";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__rosapi_msgs__msg__TypeDef() }
  }
}


