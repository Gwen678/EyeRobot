#[cfg(feature = "serde")]
use serde::{Deserialize, Serialize};


#[link(name = "rosbridge_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__rosbridge_msgs__msg__ConnectedClient() -> *const std::ffi::c_void;
}

#[link(name = "rosbridge_msgs__rosidl_generator_c")]
extern "C" {
    fn rosbridge_msgs__msg__ConnectedClient__init(msg: *mut ConnectedClient) -> bool;
    fn rosbridge_msgs__msg__ConnectedClient__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<ConnectedClient>, size: usize) -> bool;
    fn rosbridge_msgs__msg__ConnectedClient__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<ConnectedClient>);
    fn rosbridge_msgs__msg__ConnectedClient__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<ConnectedClient>, out_seq: *mut rosidl_runtime_rs::Sequence<ConnectedClient>) -> bool;
}

// Corresponds to rosbridge_msgs__msg__ConnectedClient
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct ConnectedClient {

    // This member is not documented.
    #[allow(missing_docs)]
    pub ip_address: rosidl_runtime_rs::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub connection_time: builtin_interfaces::msg::rmw::Time,

}



impl Default for ConnectedClient {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !rosbridge_msgs__msg__ConnectedClient__init(&mut msg as *mut _) {
        panic!("Call to rosbridge_msgs__msg__ConnectedClient__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for ConnectedClient {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosbridge_msgs__msg__ConnectedClient__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosbridge_msgs__msg__ConnectedClient__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosbridge_msgs__msg__ConnectedClient__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for ConnectedClient {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for ConnectedClient where Self: Sized {
  const TYPE_NAME: &'static str = "rosbridge_msgs/msg/ConnectedClient";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__rosbridge_msgs__msg__ConnectedClient() }
  }
}


#[link(name = "rosbridge_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__rosbridge_msgs__msg__ConnectedClients() -> *const std::ffi::c_void;
}

#[link(name = "rosbridge_msgs__rosidl_generator_c")]
extern "C" {
    fn rosbridge_msgs__msg__ConnectedClients__init(msg: *mut ConnectedClients) -> bool;
    fn rosbridge_msgs__msg__ConnectedClients__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<ConnectedClients>, size: usize) -> bool;
    fn rosbridge_msgs__msg__ConnectedClients__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<ConnectedClients>);
    fn rosbridge_msgs__msg__ConnectedClients__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<ConnectedClients>, out_seq: *mut rosidl_runtime_rs::Sequence<ConnectedClients>) -> bool;
}

// Corresponds to rosbridge_msgs__msg__ConnectedClients
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct ConnectedClients {

    // This member is not documented.
    #[allow(missing_docs)]
    pub clients: rosidl_runtime_rs::Sequence<super::super::msg::rmw::ConnectedClient>,

}



impl Default for ConnectedClients {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !rosbridge_msgs__msg__ConnectedClients__init(&mut msg as *mut _) {
        panic!("Call to rosbridge_msgs__msg__ConnectedClients__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for ConnectedClients {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosbridge_msgs__msg__ConnectedClients__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosbridge_msgs__msg__ConnectedClients__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosbridge_msgs__msg__ConnectedClients__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for ConnectedClients {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for ConnectedClients where Self: Sized {
  const TYPE_NAME: &'static str = "rosbridge_msgs/msg/ConnectedClients";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__rosbridge_msgs__msg__ConnectedClients() }
  }
}


