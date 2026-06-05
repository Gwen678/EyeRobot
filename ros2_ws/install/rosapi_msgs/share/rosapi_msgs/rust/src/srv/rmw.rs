#[cfg(feature = "serde")]
use serde::{Deserialize, Serialize};



#[link(name = "rosapi_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__rosapi_msgs__srv__DeleteParam_Request() -> *const std::ffi::c_void;
}

#[link(name = "rosapi_msgs__rosidl_generator_c")]
extern "C" {
    fn rosapi_msgs__srv__DeleteParam_Request__init(msg: *mut DeleteParam_Request) -> bool;
    fn rosapi_msgs__srv__DeleteParam_Request__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<DeleteParam_Request>, size: usize) -> bool;
    fn rosapi_msgs__srv__DeleteParam_Request__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<DeleteParam_Request>);
    fn rosapi_msgs__srv__DeleteParam_Request__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<DeleteParam_Request>, out_seq: *mut rosidl_runtime_rs::Sequence<DeleteParam_Request>) -> bool;
}

// Corresponds to rosapi_msgs__srv__DeleteParam_Request
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct DeleteParam_Request {

    // This member is not documented.
    #[allow(missing_docs)]
    pub name: rosidl_runtime_rs::String,

}



impl Default for DeleteParam_Request {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !rosapi_msgs__srv__DeleteParam_Request__init(&mut msg as *mut _) {
        panic!("Call to rosapi_msgs__srv__DeleteParam_Request__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for DeleteParam_Request {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__DeleteParam_Request__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__DeleteParam_Request__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__DeleteParam_Request__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for DeleteParam_Request {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for DeleteParam_Request where Self: Sized {
  const TYPE_NAME: &'static str = "rosapi_msgs/srv/DeleteParam_Request";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__rosapi_msgs__srv__DeleteParam_Request() }
  }
}


#[link(name = "rosapi_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__rosapi_msgs__srv__DeleteParam_Response() -> *const std::ffi::c_void;
}

#[link(name = "rosapi_msgs__rosidl_generator_c")]
extern "C" {
    fn rosapi_msgs__srv__DeleteParam_Response__init(msg: *mut DeleteParam_Response) -> bool;
    fn rosapi_msgs__srv__DeleteParam_Response__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<DeleteParam_Response>, size: usize) -> bool;
    fn rosapi_msgs__srv__DeleteParam_Response__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<DeleteParam_Response>);
    fn rosapi_msgs__srv__DeleteParam_Response__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<DeleteParam_Response>, out_seq: *mut rosidl_runtime_rs::Sequence<DeleteParam_Response>) -> bool;
}

// Corresponds to rosapi_msgs__srv__DeleteParam_Response
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct DeleteParam_Response {

    // This member is not documented.
    #[allow(missing_docs)]
    pub structure_needs_at_least_one_member: u8,

}



impl Default for DeleteParam_Response {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !rosapi_msgs__srv__DeleteParam_Response__init(&mut msg as *mut _) {
        panic!("Call to rosapi_msgs__srv__DeleteParam_Response__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for DeleteParam_Response {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__DeleteParam_Response__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__DeleteParam_Response__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__DeleteParam_Response__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for DeleteParam_Response {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for DeleteParam_Response where Self: Sized {
  const TYPE_NAME: &'static str = "rosapi_msgs/srv/DeleteParam_Response";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__rosapi_msgs__srv__DeleteParam_Response() }
  }
}


#[link(name = "rosapi_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__rosapi_msgs__srv__GetActionServers_Request() -> *const std::ffi::c_void;
}

#[link(name = "rosapi_msgs__rosidl_generator_c")]
extern "C" {
    fn rosapi_msgs__srv__GetActionServers_Request__init(msg: *mut GetActionServers_Request) -> bool;
    fn rosapi_msgs__srv__GetActionServers_Request__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<GetActionServers_Request>, size: usize) -> bool;
    fn rosapi_msgs__srv__GetActionServers_Request__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<GetActionServers_Request>);
    fn rosapi_msgs__srv__GetActionServers_Request__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<GetActionServers_Request>, out_seq: *mut rosidl_runtime_rs::Sequence<GetActionServers_Request>) -> bool;
}

// Corresponds to rosapi_msgs__srv__GetActionServers_Request
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct GetActionServers_Request {

    // This member is not documented.
    #[allow(missing_docs)]
    pub structure_needs_at_least_one_member: u8,

}



impl Default for GetActionServers_Request {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !rosapi_msgs__srv__GetActionServers_Request__init(&mut msg as *mut _) {
        panic!("Call to rosapi_msgs__srv__GetActionServers_Request__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for GetActionServers_Request {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__GetActionServers_Request__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__GetActionServers_Request__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__GetActionServers_Request__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for GetActionServers_Request {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for GetActionServers_Request where Self: Sized {
  const TYPE_NAME: &'static str = "rosapi_msgs/srv/GetActionServers_Request";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__rosapi_msgs__srv__GetActionServers_Request() }
  }
}


#[link(name = "rosapi_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__rosapi_msgs__srv__GetActionServers_Response() -> *const std::ffi::c_void;
}

#[link(name = "rosapi_msgs__rosidl_generator_c")]
extern "C" {
    fn rosapi_msgs__srv__GetActionServers_Response__init(msg: *mut GetActionServers_Response) -> bool;
    fn rosapi_msgs__srv__GetActionServers_Response__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<GetActionServers_Response>, size: usize) -> bool;
    fn rosapi_msgs__srv__GetActionServers_Response__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<GetActionServers_Response>);
    fn rosapi_msgs__srv__GetActionServers_Response__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<GetActionServers_Response>, out_seq: *mut rosidl_runtime_rs::Sequence<GetActionServers_Response>) -> bool;
}

// Corresponds to rosapi_msgs__srv__GetActionServers_Response
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct GetActionServers_Response {

    // This member is not documented.
    #[allow(missing_docs)]
    pub action_servers: rosidl_runtime_rs::Sequence<rosidl_runtime_rs::String>,

}



impl Default for GetActionServers_Response {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !rosapi_msgs__srv__GetActionServers_Response__init(&mut msg as *mut _) {
        panic!("Call to rosapi_msgs__srv__GetActionServers_Response__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for GetActionServers_Response {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__GetActionServers_Response__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__GetActionServers_Response__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__GetActionServers_Response__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for GetActionServers_Response {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for GetActionServers_Response where Self: Sized {
  const TYPE_NAME: &'static str = "rosapi_msgs/srv/GetActionServers_Response";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__rosapi_msgs__srv__GetActionServers_Response() }
  }
}


#[link(name = "rosapi_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__rosapi_msgs__srv__GetParam_Request() -> *const std::ffi::c_void;
}

#[link(name = "rosapi_msgs__rosidl_generator_c")]
extern "C" {
    fn rosapi_msgs__srv__GetParam_Request__init(msg: *mut GetParam_Request) -> bool;
    fn rosapi_msgs__srv__GetParam_Request__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<GetParam_Request>, size: usize) -> bool;
    fn rosapi_msgs__srv__GetParam_Request__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<GetParam_Request>);
    fn rosapi_msgs__srv__GetParam_Request__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<GetParam_Request>, out_seq: *mut rosidl_runtime_rs::Sequence<GetParam_Request>) -> bool;
}

// Corresponds to rosapi_msgs__srv__GetParam_Request
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct GetParam_Request {

    // This member is not documented.
    #[allow(missing_docs)]
    pub name: rosidl_runtime_rs::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub default_value: rosidl_runtime_rs::String,

}



impl Default for GetParam_Request {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !rosapi_msgs__srv__GetParam_Request__init(&mut msg as *mut _) {
        panic!("Call to rosapi_msgs__srv__GetParam_Request__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for GetParam_Request {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__GetParam_Request__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__GetParam_Request__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__GetParam_Request__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for GetParam_Request {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for GetParam_Request where Self: Sized {
  const TYPE_NAME: &'static str = "rosapi_msgs/srv/GetParam_Request";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__rosapi_msgs__srv__GetParam_Request() }
  }
}


#[link(name = "rosapi_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__rosapi_msgs__srv__GetParam_Response() -> *const std::ffi::c_void;
}

#[link(name = "rosapi_msgs__rosidl_generator_c")]
extern "C" {
    fn rosapi_msgs__srv__GetParam_Response__init(msg: *mut GetParam_Response) -> bool;
    fn rosapi_msgs__srv__GetParam_Response__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<GetParam_Response>, size: usize) -> bool;
    fn rosapi_msgs__srv__GetParam_Response__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<GetParam_Response>);
    fn rosapi_msgs__srv__GetParam_Response__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<GetParam_Response>, out_seq: *mut rosidl_runtime_rs::Sequence<GetParam_Response>) -> bool;
}

// Corresponds to rosapi_msgs__srv__GetParam_Response
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct GetParam_Response {

    // This member is not documented.
    #[allow(missing_docs)]
    pub value: rosidl_runtime_rs::String,

}



impl Default for GetParam_Response {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !rosapi_msgs__srv__GetParam_Response__init(&mut msg as *mut _) {
        panic!("Call to rosapi_msgs__srv__GetParam_Response__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for GetParam_Response {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__GetParam_Response__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__GetParam_Response__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__GetParam_Response__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for GetParam_Response {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for GetParam_Response where Self: Sized {
  const TYPE_NAME: &'static str = "rosapi_msgs/srv/GetParam_Response";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__rosapi_msgs__srv__GetParam_Response() }
  }
}


#[link(name = "rosapi_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__rosapi_msgs__srv__GetParamNames_Request() -> *const std::ffi::c_void;
}

#[link(name = "rosapi_msgs__rosidl_generator_c")]
extern "C" {
    fn rosapi_msgs__srv__GetParamNames_Request__init(msg: *mut GetParamNames_Request) -> bool;
    fn rosapi_msgs__srv__GetParamNames_Request__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<GetParamNames_Request>, size: usize) -> bool;
    fn rosapi_msgs__srv__GetParamNames_Request__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<GetParamNames_Request>);
    fn rosapi_msgs__srv__GetParamNames_Request__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<GetParamNames_Request>, out_seq: *mut rosidl_runtime_rs::Sequence<GetParamNames_Request>) -> bool;
}

// Corresponds to rosapi_msgs__srv__GetParamNames_Request
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct GetParamNames_Request {

    // This member is not documented.
    #[allow(missing_docs)]
    pub structure_needs_at_least_one_member: u8,

}



impl Default for GetParamNames_Request {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !rosapi_msgs__srv__GetParamNames_Request__init(&mut msg as *mut _) {
        panic!("Call to rosapi_msgs__srv__GetParamNames_Request__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for GetParamNames_Request {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__GetParamNames_Request__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__GetParamNames_Request__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__GetParamNames_Request__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for GetParamNames_Request {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for GetParamNames_Request where Self: Sized {
  const TYPE_NAME: &'static str = "rosapi_msgs/srv/GetParamNames_Request";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__rosapi_msgs__srv__GetParamNames_Request() }
  }
}


#[link(name = "rosapi_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__rosapi_msgs__srv__GetParamNames_Response() -> *const std::ffi::c_void;
}

#[link(name = "rosapi_msgs__rosidl_generator_c")]
extern "C" {
    fn rosapi_msgs__srv__GetParamNames_Response__init(msg: *mut GetParamNames_Response) -> bool;
    fn rosapi_msgs__srv__GetParamNames_Response__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<GetParamNames_Response>, size: usize) -> bool;
    fn rosapi_msgs__srv__GetParamNames_Response__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<GetParamNames_Response>);
    fn rosapi_msgs__srv__GetParamNames_Response__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<GetParamNames_Response>, out_seq: *mut rosidl_runtime_rs::Sequence<GetParamNames_Response>) -> bool;
}

// Corresponds to rosapi_msgs__srv__GetParamNames_Response
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct GetParamNames_Response {

    // This member is not documented.
    #[allow(missing_docs)]
    pub names: rosidl_runtime_rs::Sequence<rosidl_runtime_rs::String>,

}



impl Default for GetParamNames_Response {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !rosapi_msgs__srv__GetParamNames_Response__init(&mut msg as *mut _) {
        panic!("Call to rosapi_msgs__srv__GetParamNames_Response__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for GetParamNames_Response {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__GetParamNames_Response__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__GetParamNames_Response__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__GetParamNames_Response__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for GetParamNames_Response {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for GetParamNames_Response where Self: Sized {
  const TYPE_NAME: &'static str = "rosapi_msgs/srv/GetParamNames_Response";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__rosapi_msgs__srv__GetParamNames_Response() }
  }
}


#[link(name = "rosapi_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__rosapi_msgs__srv__GetROSVersion_Request() -> *const std::ffi::c_void;
}

#[link(name = "rosapi_msgs__rosidl_generator_c")]
extern "C" {
    fn rosapi_msgs__srv__GetROSVersion_Request__init(msg: *mut GetROSVersion_Request) -> bool;
    fn rosapi_msgs__srv__GetROSVersion_Request__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<GetROSVersion_Request>, size: usize) -> bool;
    fn rosapi_msgs__srv__GetROSVersion_Request__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<GetROSVersion_Request>);
    fn rosapi_msgs__srv__GetROSVersion_Request__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<GetROSVersion_Request>, out_seq: *mut rosidl_runtime_rs::Sequence<GetROSVersion_Request>) -> bool;
}

// Corresponds to rosapi_msgs__srv__GetROSVersion_Request
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct GetROSVersion_Request {

    // This member is not documented.
    #[allow(missing_docs)]
    pub structure_needs_at_least_one_member: u8,

}



impl Default for GetROSVersion_Request {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !rosapi_msgs__srv__GetROSVersion_Request__init(&mut msg as *mut _) {
        panic!("Call to rosapi_msgs__srv__GetROSVersion_Request__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for GetROSVersion_Request {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__GetROSVersion_Request__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__GetROSVersion_Request__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__GetROSVersion_Request__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for GetROSVersion_Request {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for GetROSVersion_Request where Self: Sized {
  const TYPE_NAME: &'static str = "rosapi_msgs/srv/GetROSVersion_Request";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__rosapi_msgs__srv__GetROSVersion_Request() }
  }
}


#[link(name = "rosapi_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__rosapi_msgs__srv__GetROSVersion_Response() -> *const std::ffi::c_void;
}

#[link(name = "rosapi_msgs__rosidl_generator_c")]
extern "C" {
    fn rosapi_msgs__srv__GetROSVersion_Response__init(msg: *mut GetROSVersion_Response) -> bool;
    fn rosapi_msgs__srv__GetROSVersion_Response__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<GetROSVersion_Response>, size: usize) -> bool;
    fn rosapi_msgs__srv__GetROSVersion_Response__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<GetROSVersion_Response>);
    fn rosapi_msgs__srv__GetROSVersion_Response__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<GetROSVersion_Response>, out_seq: *mut rosidl_runtime_rs::Sequence<GetROSVersion_Response>) -> bool;
}

// Corresponds to rosapi_msgs__srv__GetROSVersion_Response
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct GetROSVersion_Response {

    // This member is not documented.
    #[allow(missing_docs)]
    pub version: u8,


    // This member is not documented.
    #[allow(missing_docs)]
    pub distro: rosidl_runtime_rs::String,

}



impl Default for GetROSVersion_Response {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !rosapi_msgs__srv__GetROSVersion_Response__init(&mut msg as *mut _) {
        panic!("Call to rosapi_msgs__srv__GetROSVersion_Response__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for GetROSVersion_Response {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__GetROSVersion_Response__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__GetROSVersion_Response__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__GetROSVersion_Response__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for GetROSVersion_Response {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for GetROSVersion_Response where Self: Sized {
  const TYPE_NAME: &'static str = "rosapi_msgs/srv/GetROSVersion_Response";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__rosapi_msgs__srv__GetROSVersion_Response() }
  }
}


#[link(name = "rosapi_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__rosapi_msgs__srv__GetTime_Request() -> *const std::ffi::c_void;
}

#[link(name = "rosapi_msgs__rosidl_generator_c")]
extern "C" {
    fn rosapi_msgs__srv__GetTime_Request__init(msg: *mut GetTime_Request) -> bool;
    fn rosapi_msgs__srv__GetTime_Request__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<GetTime_Request>, size: usize) -> bool;
    fn rosapi_msgs__srv__GetTime_Request__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<GetTime_Request>);
    fn rosapi_msgs__srv__GetTime_Request__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<GetTime_Request>, out_seq: *mut rosidl_runtime_rs::Sequence<GetTime_Request>) -> bool;
}

// Corresponds to rosapi_msgs__srv__GetTime_Request
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct GetTime_Request {

    // This member is not documented.
    #[allow(missing_docs)]
    pub structure_needs_at_least_one_member: u8,

}



impl Default for GetTime_Request {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !rosapi_msgs__srv__GetTime_Request__init(&mut msg as *mut _) {
        panic!("Call to rosapi_msgs__srv__GetTime_Request__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for GetTime_Request {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__GetTime_Request__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__GetTime_Request__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__GetTime_Request__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for GetTime_Request {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for GetTime_Request where Self: Sized {
  const TYPE_NAME: &'static str = "rosapi_msgs/srv/GetTime_Request";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__rosapi_msgs__srv__GetTime_Request() }
  }
}


#[link(name = "rosapi_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__rosapi_msgs__srv__GetTime_Response() -> *const std::ffi::c_void;
}

#[link(name = "rosapi_msgs__rosidl_generator_c")]
extern "C" {
    fn rosapi_msgs__srv__GetTime_Response__init(msg: *mut GetTime_Response) -> bool;
    fn rosapi_msgs__srv__GetTime_Response__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<GetTime_Response>, size: usize) -> bool;
    fn rosapi_msgs__srv__GetTime_Response__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<GetTime_Response>);
    fn rosapi_msgs__srv__GetTime_Response__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<GetTime_Response>, out_seq: *mut rosidl_runtime_rs::Sequence<GetTime_Response>) -> bool;
}

// Corresponds to rosapi_msgs__srv__GetTime_Response
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct GetTime_Response {

    // This member is not documented.
    #[allow(missing_docs)]
    pub time: builtin_interfaces::msg::rmw::Time,

}



impl Default for GetTime_Response {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !rosapi_msgs__srv__GetTime_Response__init(&mut msg as *mut _) {
        panic!("Call to rosapi_msgs__srv__GetTime_Response__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for GetTime_Response {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__GetTime_Response__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__GetTime_Response__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__GetTime_Response__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for GetTime_Response {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for GetTime_Response where Self: Sized {
  const TYPE_NAME: &'static str = "rosapi_msgs/srv/GetTime_Response";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__rosapi_msgs__srv__GetTime_Response() }
  }
}


#[link(name = "rosapi_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__rosapi_msgs__srv__HasParam_Request() -> *const std::ffi::c_void;
}

#[link(name = "rosapi_msgs__rosidl_generator_c")]
extern "C" {
    fn rosapi_msgs__srv__HasParam_Request__init(msg: *mut HasParam_Request) -> bool;
    fn rosapi_msgs__srv__HasParam_Request__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<HasParam_Request>, size: usize) -> bool;
    fn rosapi_msgs__srv__HasParam_Request__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<HasParam_Request>);
    fn rosapi_msgs__srv__HasParam_Request__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<HasParam_Request>, out_seq: *mut rosidl_runtime_rs::Sequence<HasParam_Request>) -> bool;
}

// Corresponds to rosapi_msgs__srv__HasParam_Request
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct HasParam_Request {

    // This member is not documented.
    #[allow(missing_docs)]
    pub name: rosidl_runtime_rs::String,

}



impl Default for HasParam_Request {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !rosapi_msgs__srv__HasParam_Request__init(&mut msg as *mut _) {
        panic!("Call to rosapi_msgs__srv__HasParam_Request__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for HasParam_Request {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__HasParam_Request__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__HasParam_Request__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__HasParam_Request__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for HasParam_Request {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for HasParam_Request where Self: Sized {
  const TYPE_NAME: &'static str = "rosapi_msgs/srv/HasParam_Request";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__rosapi_msgs__srv__HasParam_Request() }
  }
}


#[link(name = "rosapi_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__rosapi_msgs__srv__HasParam_Response() -> *const std::ffi::c_void;
}

#[link(name = "rosapi_msgs__rosidl_generator_c")]
extern "C" {
    fn rosapi_msgs__srv__HasParam_Response__init(msg: *mut HasParam_Response) -> bool;
    fn rosapi_msgs__srv__HasParam_Response__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<HasParam_Response>, size: usize) -> bool;
    fn rosapi_msgs__srv__HasParam_Response__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<HasParam_Response>);
    fn rosapi_msgs__srv__HasParam_Response__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<HasParam_Response>, out_seq: *mut rosidl_runtime_rs::Sequence<HasParam_Response>) -> bool;
}

// Corresponds to rosapi_msgs__srv__HasParam_Response
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct HasParam_Response {

    // This member is not documented.
    #[allow(missing_docs)]
    pub exists: bool,

}



impl Default for HasParam_Response {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !rosapi_msgs__srv__HasParam_Response__init(&mut msg as *mut _) {
        panic!("Call to rosapi_msgs__srv__HasParam_Response__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for HasParam_Response {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__HasParam_Response__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__HasParam_Response__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__HasParam_Response__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for HasParam_Response {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for HasParam_Response where Self: Sized {
  const TYPE_NAME: &'static str = "rosapi_msgs/srv/HasParam_Response";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__rosapi_msgs__srv__HasParam_Response() }
  }
}


#[link(name = "rosapi_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__rosapi_msgs__srv__MessageDetails_Request() -> *const std::ffi::c_void;
}

#[link(name = "rosapi_msgs__rosidl_generator_c")]
extern "C" {
    fn rosapi_msgs__srv__MessageDetails_Request__init(msg: *mut MessageDetails_Request) -> bool;
    fn rosapi_msgs__srv__MessageDetails_Request__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<MessageDetails_Request>, size: usize) -> bool;
    fn rosapi_msgs__srv__MessageDetails_Request__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<MessageDetails_Request>);
    fn rosapi_msgs__srv__MessageDetails_Request__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<MessageDetails_Request>, out_seq: *mut rosidl_runtime_rs::Sequence<MessageDetails_Request>) -> bool;
}

// Corresponds to rosapi_msgs__srv__MessageDetails_Request
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct MessageDetails_Request {

    // This member is not documented.
    #[allow(missing_docs)]
    pub type_: rosidl_runtime_rs::String,

}



impl Default for MessageDetails_Request {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !rosapi_msgs__srv__MessageDetails_Request__init(&mut msg as *mut _) {
        panic!("Call to rosapi_msgs__srv__MessageDetails_Request__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for MessageDetails_Request {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__MessageDetails_Request__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__MessageDetails_Request__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__MessageDetails_Request__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for MessageDetails_Request {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for MessageDetails_Request where Self: Sized {
  const TYPE_NAME: &'static str = "rosapi_msgs/srv/MessageDetails_Request";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__rosapi_msgs__srv__MessageDetails_Request() }
  }
}


#[link(name = "rosapi_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__rosapi_msgs__srv__MessageDetails_Response() -> *const std::ffi::c_void;
}

#[link(name = "rosapi_msgs__rosidl_generator_c")]
extern "C" {
    fn rosapi_msgs__srv__MessageDetails_Response__init(msg: *mut MessageDetails_Response) -> bool;
    fn rosapi_msgs__srv__MessageDetails_Response__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<MessageDetails_Response>, size: usize) -> bool;
    fn rosapi_msgs__srv__MessageDetails_Response__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<MessageDetails_Response>);
    fn rosapi_msgs__srv__MessageDetails_Response__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<MessageDetails_Response>, out_seq: *mut rosidl_runtime_rs::Sequence<MessageDetails_Response>) -> bool;
}

// Corresponds to rosapi_msgs__srv__MessageDetails_Response
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct MessageDetails_Response {

    // This member is not documented.
    #[allow(missing_docs)]
    pub typedefs: rosidl_runtime_rs::Sequence<super::super::msg::rmw::TypeDef>,

}



impl Default for MessageDetails_Response {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !rosapi_msgs__srv__MessageDetails_Response__init(&mut msg as *mut _) {
        panic!("Call to rosapi_msgs__srv__MessageDetails_Response__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for MessageDetails_Response {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__MessageDetails_Response__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__MessageDetails_Response__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__MessageDetails_Response__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for MessageDetails_Response {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for MessageDetails_Response where Self: Sized {
  const TYPE_NAME: &'static str = "rosapi_msgs/srv/MessageDetails_Response";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__rosapi_msgs__srv__MessageDetails_Response() }
  }
}


#[link(name = "rosapi_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__rosapi_msgs__srv__Nodes_Request() -> *const std::ffi::c_void;
}

#[link(name = "rosapi_msgs__rosidl_generator_c")]
extern "C" {
    fn rosapi_msgs__srv__Nodes_Request__init(msg: *mut Nodes_Request) -> bool;
    fn rosapi_msgs__srv__Nodes_Request__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<Nodes_Request>, size: usize) -> bool;
    fn rosapi_msgs__srv__Nodes_Request__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<Nodes_Request>);
    fn rosapi_msgs__srv__Nodes_Request__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<Nodes_Request>, out_seq: *mut rosidl_runtime_rs::Sequence<Nodes_Request>) -> bool;
}

// Corresponds to rosapi_msgs__srv__Nodes_Request
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Nodes_Request {

    // This member is not documented.
    #[allow(missing_docs)]
    pub structure_needs_at_least_one_member: u8,

}



impl Default for Nodes_Request {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !rosapi_msgs__srv__Nodes_Request__init(&mut msg as *mut _) {
        panic!("Call to rosapi_msgs__srv__Nodes_Request__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for Nodes_Request {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__Nodes_Request__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__Nodes_Request__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__Nodes_Request__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for Nodes_Request {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for Nodes_Request where Self: Sized {
  const TYPE_NAME: &'static str = "rosapi_msgs/srv/Nodes_Request";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__rosapi_msgs__srv__Nodes_Request() }
  }
}


#[link(name = "rosapi_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__rosapi_msgs__srv__Nodes_Response() -> *const std::ffi::c_void;
}

#[link(name = "rosapi_msgs__rosidl_generator_c")]
extern "C" {
    fn rosapi_msgs__srv__Nodes_Response__init(msg: *mut Nodes_Response) -> bool;
    fn rosapi_msgs__srv__Nodes_Response__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<Nodes_Response>, size: usize) -> bool;
    fn rosapi_msgs__srv__Nodes_Response__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<Nodes_Response>);
    fn rosapi_msgs__srv__Nodes_Response__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<Nodes_Response>, out_seq: *mut rosidl_runtime_rs::Sequence<Nodes_Response>) -> bool;
}

// Corresponds to rosapi_msgs__srv__Nodes_Response
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Nodes_Response {

    // This member is not documented.
    #[allow(missing_docs)]
    pub nodes: rosidl_runtime_rs::Sequence<rosidl_runtime_rs::String>,

}



impl Default for Nodes_Response {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !rosapi_msgs__srv__Nodes_Response__init(&mut msg as *mut _) {
        panic!("Call to rosapi_msgs__srv__Nodes_Response__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for Nodes_Response {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__Nodes_Response__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__Nodes_Response__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__Nodes_Response__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for Nodes_Response {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for Nodes_Response where Self: Sized {
  const TYPE_NAME: &'static str = "rosapi_msgs/srv/Nodes_Response";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__rosapi_msgs__srv__Nodes_Response() }
  }
}


#[link(name = "rosapi_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__rosapi_msgs__srv__NodeDetails_Request() -> *const std::ffi::c_void;
}

#[link(name = "rosapi_msgs__rosidl_generator_c")]
extern "C" {
    fn rosapi_msgs__srv__NodeDetails_Request__init(msg: *mut NodeDetails_Request) -> bool;
    fn rosapi_msgs__srv__NodeDetails_Request__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<NodeDetails_Request>, size: usize) -> bool;
    fn rosapi_msgs__srv__NodeDetails_Request__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<NodeDetails_Request>);
    fn rosapi_msgs__srv__NodeDetails_Request__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<NodeDetails_Request>, out_seq: *mut rosidl_runtime_rs::Sequence<NodeDetails_Request>) -> bool;
}

// Corresponds to rosapi_msgs__srv__NodeDetails_Request
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct NodeDetails_Request {

    // This member is not documented.
    #[allow(missing_docs)]
    pub node: rosidl_runtime_rs::String,

}



impl Default for NodeDetails_Request {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !rosapi_msgs__srv__NodeDetails_Request__init(&mut msg as *mut _) {
        panic!("Call to rosapi_msgs__srv__NodeDetails_Request__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for NodeDetails_Request {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__NodeDetails_Request__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__NodeDetails_Request__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__NodeDetails_Request__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for NodeDetails_Request {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for NodeDetails_Request where Self: Sized {
  const TYPE_NAME: &'static str = "rosapi_msgs/srv/NodeDetails_Request";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__rosapi_msgs__srv__NodeDetails_Request() }
  }
}


#[link(name = "rosapi_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__rosapi_msgs__srv__NodeDetails_Response() -> *const std::ffi::c_void;
}

#[link(name = "rosapi_msgs__rosidl_generator_c")]
extern "C" {
    fn rosapi_msgs__srv__NodeDetails_Response__init(msg: *mut NodeDetails_Response) -> bool;
    fn rosapi_msgs__srv__NodeDetails_Response__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<NodeDetails_Response>, size: usize) -> bool;
    fn rosapi_msgs__srv__NodeDetails_Response__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<NodeDetails_Response>);
    fn rosapi_msgs__srv__NodeDetails_Response__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<NodeDetails_Response>, out_seq: *mut rosidl_runtime_rs::Sequence<NodeDetails_Response>) -> bool;
}

// Corresponds to rosapi_msgs__srv__NodeDetails_Response
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct NodeDetails_Response {

    // This member is not documented.
    #[allow(missing_docs)]
    pub subscribing: rosidl_runtime_rs::Sequence<rosidl_runtime_rs::String>,


    // This member is not documented.
    #[allow(missing_docs)]
    pub publishing: rosidl_runtime_rs::Sequence<rosidl_runtime_rs::String>,


    // This member is not documented.
    #[allow(missing_docs)]
    pub services: rosidl_runtime_rs::Sequence<rosidl_runtime_rs::String>,

}



impl Default for NodeDetails_Response {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !rosapi_msgs__srv__NodeDetails_Response__init(&mut msg as *mut _) {
        panic!("Call to rosapi_msgs__srv__NodeDetails_Response__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for NodeDetails_Response {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__NodeDetails_Response__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__NodeDetails_Response__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__NodeDetails_Response__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for NodeDetails_Response {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for NodeDetails_Response where Self: Sized {
  const TYPE_NAME: &'static str = "rosapi_msgs/srv/NodeDetails_Response";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__rosapi_msgs__srv__NodeDetails_Response() }
  }
}


#[link(name = "rosapi_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__rosapi_msgs__srv__Publishers_Request() -> *const std::ffi::c_void;
}

#[link(name = "rosapi_msgs__rosidl_generator_c")]
extern "C" {
    fn rosapi_msgs__srv__Publishers_Request__init(msg: *mut Publishers_Request) -> bool;
    fn rosapi_msgs__srv__Publishers_Request__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<Publishers_Request>, size: usize) -> bool;
    fn rosapi_msgs__srv__Publishers_Request__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<Publishers_Request>);
    fn rosapi_msgs__srv__Publishers_Request__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<Publishers_Request>, out_seq: *mut rosidl_runtime_rs::Sequence<Publishers_Request>) -> bool;
}

// Corresponds to rosapi_msgs__srv__Publishers_Request
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Publishers_Request {

    // This member is not documented.
    #[allow(missing_docs)]
    pub topic: rosidl_runtime_rs::String,

}



impl Default for Publishers_Request {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !rosapi_msgs__srv__Publishers_Request__init(&mut msg as *mut _) {
        panic!("Call to rosapi_msgs__srv__Publishers_Request__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for Publishers_Request {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__Publishers_Request__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__Publishers_Request__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__Publishers_Request__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for Publishers_Request {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for Publishers_Request where Self: Sized {
  const TYPE_NAME: &'static str = "rosapi_msgs/srv/Publishers_Request";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__rosapi_msgs__srv__Publishers_Request() }
  }
}


#[link(name = "rosapi_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__rosapi_msgs__srv__Publishers_Response() -> *const std::ffi::c_void;
}

#[link(name = "rosapi_msgs__rosidl_generator_c")]
extern "C" {
    fn rosapi_msgs__srv__Publishers_Response__init(msg: *mut Publishers_Response) -> bool;
    fn rosapi_msgs__srv__Publishers_Response__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<Publishers_Response>, size: usize) -> bool;
    fn rosapi_msgs__srv__Publishers_Response__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<Publishers_Response>);
    fn rosapi_msgs__srv__Publishers_Response__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<Publishers_Response>, out_seq: *mut rosidl_runtime_rs::Sequence<Publishers_Response>) -> bool;
}

// Corresponds to rosapi_msgs__srv__Publishers_Response
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Publishers_Response {

    // This member is not documented.
    #[allow(missing_docs)]
    pub publishers: rosidl_runtime_rs::Sequence<rosidl_runtime_rs::String>,

}



impl Default for Publishers_Response {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !rosapi_msgs__srv__Publishers_Response__init(&mut msg as *mut _) {
        panic!("Call to rosapi_msgs__srv__Publishers_Response__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for Publishers_Response {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__Publishers_Response__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__Publishers_Response__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__Publishers_Response__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for Publishers_Response {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for Publishers_Response where Self: Sized {
  const TYPE_NAME: &'static str = "rosapi_msgs/srv/Publishers_Response";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__rosapi_msgs__srv__Publishers_Response() }
  }
}


#[link(name = "rosapi_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__rosapi_msgs__srv__ServiceNode_Request() -> *const std::ffi::c_void;
}

#[link(name = "rosapi_msgs__rosidl_generator_c")]
extern "C" {
    fn rosapi_msgs__srv__ServiceNode_Request__init(msg: *mut ServiceNode_Request) -> bool;
    fn rosapi_msgs__srv__ServiceNode_Request__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<ServiceNode_Request>, size: usize) -> bool;
    fn rosapi_msgs__srv__ServiceNode_Request__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<ServiceNode_Request>);
    fn rosapi_msgs__srv__ServiceNode_Request__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<ServiceNode_Request>, out_seq: *mut rosidl_runtime_rs::Sequence<ServiceNode_Request>) -> bool;
}

// Corresponds to rosapi_msgs__srv__ServiceNode_Request
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct ServiceNode_Request {

    // This member is not documented.
    #[allow(missing_docs)]
    pub service: rosidl_runtime_rs::String,

}



impl Default for ServiceNode_Request {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !rosapi_msgs__srv__ServiceNode_Request__init(&mut msg as *mut _) {
        panic!("Call to rosapi_msgs__srv__ServiceNode_Request__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for ServiceNode_Request {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__ServiceNode_Request__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__ServiceNode_Request__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__ServiceNode_Request__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for ServiceNode_Request {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for ServiceNode_Request where Self: Sized {
  const TYPE_NAME: &'static str = "rosapi_msgs/srv/ServiceNode_Request";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__rosapi_msgs__srv__ServiceNode_Request() }
  }
}


#[link(name = "rosapi_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__rosapi_msgs__srv__ServiceNode_Response() -> *const std::ffi::c_void;
}

#[link(name = "rosapi_msgs__rosidl_generator_c")]
extern "C" {
    fn rosapi_msgs__srv__ServiceNode_Response__init(msg: *mut ServiceNode_Response) -> bool;
    fn rosapi_msgs__srv__ServiceNode_Response__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<ServiceNode_Response>, size: usize) -> bool;
    fn rosapi_msgs__srv__ServiceNode_Response__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<ServiceNode_Response>);
    fn rosapi_msgs__srv__ServiceNode_Response__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<ServiceNode_Response>, out_seq: *mut rosidl_runtime_rs::Sequence<ServiceNode_Response>) -> bool;
}

// Corresponds to rosapi_msgs__srv__ServiceNode_Response
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct ServiceNode_Response {

    // This member is not documented.
    #[allow(missing_docs)]
    pub node: rosidl_runtime_rs::String,

}



impl Default for ServiceNode_Response {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !rosapi_msgs__srv__ServiceNode_Response__init(&mut msg as *mut _) {
        panic!("Call to rosapi_msgs__srv__ServiceNode_Response__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for ServiceNode_Response {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__ServiceNode_Response__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__ServiceNode_Response__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__ServiceNode_Response__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for ServiceNode_Response {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for ServiceNode_Response where Self: Sized {
  const TYPE_NAME: &'static str = "rosapi_msgs/srv/ServiceNode_Response";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__rosapi_msgs__srv__ServiceNode_Response() }
  }
}


#[link(name = "rosapi_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__rosapi_msgs__srv__ServiceProviders_Request() -> *const std::ffi::c_void;
}

#[link(name = "rosapi_msgs__rosidl_generator_c")]
extern "C" {
    fn rosapi_msgs__srv__ServiceProviders_Request__init(msg: *mut ServiceProviders_Request) -> bool;
    fn rosapi_msgs__srv__ServiceProviders_Request__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<ServiceProviders_Request>, size: usize) -> bool;
    fn rosapi_msgs__srv__ServiceProviders_Request__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<ServiceProviders_Request>);
    fn rosapi_msgs__srv__ServiceProviders_Request__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<ServiceProviders_Request>, out_seq: *mut rosidl_runtime_rs::Sequence<ServiceProviders_Request>) -> bool;
}

// Corresponds to rosapi_msgs__srv__ServiceProviders_Request
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct ServiceProviders_Request {

    // This member is not documented.
    #[allow(missing_docs)]
    pub service: rosidl_runtime_rs::String,

}



impl Default for ServiceProviders_Request {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !rosapi_msgs__srv__ServiceProviders_Request__init(&mut msg as *mut _) {
        panic!("Call to rosapi_msgs__srv__ServiceProviders_Request__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for ServiceProviders_Request {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__ServiceProviders_Request__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__ServiceProviders_Request__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__ServiceProviders_Request__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for ServiceProviders_Request {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for ServiceProviders_Request where Self: Sized {
  const TYPE_NAME: &'static str = "rosapi_msgs/srv/ServiceProviders_Request";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__rosapi_msgs__srv__ServiceProviders_Request() }
  }
}


#[link(name = "rosapi_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__rosapi_msgs__srv__ServiceProviders_Response() -> *const std::ffi::c_void;
}

#[link(name = "rosapi_msgs__rosidl_generator_c")]
extern "C" {
    fn rosapi_msgs__srv__ServiceProviders_Response__init(msg: *mut ServiceProviders_Response) -> bool;
    fn rosapi_msgs__srv__ServiceProviders_Response__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<ServiceProviders_Response>, size: usize) -> bool;
    fn rosapi_msgs__srv__ServiceProviders_Response__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<ServiceProviders_Response>);
    fn rosapi_msgs__srv__ServiceProviders_Response__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<ServiceProviders_Response>, out_seq: *mut rosidl_runtime_rs::Sequence<ServiceProviders_Response>) -> bool;
}

// Corresponds to rosapi_msgs__srv__ServiceProviders_Response
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct ServiceProviders_Response {

    // This member is not documented.
    #[allow(missing_docs)]
    pub providers: rosidl_runtime_rs::Sequence<rosidl_runtime_rs::String>,

}



impl Default for ServiceProviders_Response {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !rosapi_msgs__srv__ServiceProviders_Response__init(&mut msg as *mut _) {
        panic!("Call to rosapi_msgs__srv__ServiceProviders_Response__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for ServiceProviders_Response {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__ServiceProviders_Response__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__ServiceProviders_Response__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__ServiceProviders_Response__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for ServiceProviders_Response {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for ServiceProviders_Response where Self: Sized {
  const TYPE_NAME: &'static str = "rosapi_msgs/srv/ServiceProviders_Response";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__rosapi_msgs__srv__ServiceProviders_Response() }
  }
}


#[link(name = "rosapi_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__rosapi_msgs__srv__ServiceRequestDetails_Request() -> *const std::ffi::c_void;
}

#[link(name = "rosapi_msgs__rosidl_generator_c")]
extern "C" {
    fn rosapi_msgs__srv__ServiceRequestDetails_Request__init(msg: *mut ServiceRequestDetails_Request) -> bool;
    fn rosapi_msgs__srv__ServiceRequestDetails_Request__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<ServiceRequestDetails_Request>, size: usize) -> bool;
    fn rosapi_msgs__srv__ServiceRequestDetails_Request__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<ServiceRequestDetails_Request>);
    fn rosapi_msgs__srv__ServiceRequestDetails_Request__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<ServiceRequestDetails_Request>, out_seq: *mut rosidl_runtime_rs::Sequence<ServiceRequestDetails_Request>) -> bool;
}

// Corresponds to rosapi_msgs__srv__ServiceRequestDetails_Request
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct ServiceRequestDetails_Request {

    // This member is not documented.
    #[allow(missing_docs)]
    pub type_: rosidl_runtime_rs::String,

}



impl Default for ServiceRequestDetails_Request {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !rosapi_msgs__srv__ServiceRequestDetails_Request__init(&mut msg as *mut _) {
        panic!("Call to rosapi_msgs__srv__ServiceRequestDetails_Request__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for ServiceRequestDetails_Request {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__ServiceRequestDetails_Request__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__ServiceRequestDetails_Request__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__ServiceRequestDetails_Request__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for ServiceRequestDetails_Request {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for ServiceRequestDetails_Request where Self: Sized {
  const TYPE_NAME: &'static str = "rosapi_msgs/srv/ServiceRequestDetails_Request";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__rosapi_msgs__srv__ServiceRequestDetails_Request() }
  }
}


#[link(name = "rosapi_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__rosapi_msgs__srv__ServiceRequestDetails_Response() -> *const std::ffi::c_void;
}

#[link(name = "rosapi_msgs__rosidl_generator_c")]
extern "C" {
    fn rosapi_msgs__srv__ServiceRequestDetails_Response__init(msg: *mut ServiceRequestDetails_Response) -> bool;
    fn rosapi_msgs__srv__ServiceRequestDetails_Response__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<ServiceRequestDetails_Response>, size: usize) -> bool;
    fn rosapi_msgs__srv__ServiceRequestDetails_Response__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<ServiceRequestDetails_Response>);
    fn rosapi_msgs__srv__ServiceRequestDetails_Response__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<ServiceRequestDetails_Response>, out_seq: *mut rosidl_runtime_rs::Sequence<ServiceRequestDetails_Response>) -> bool;
}

// Corresponds to rosapi_msgs__srv__ServiceRequestDetails_Response
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct ServiceRequestDetails_Response {

    // This member is not documented.
    #[allow(missing_docs)]
    pub typedefs: rosidl_runtime_rs::Sequence<super::super::msg::rmw::TypeDef>,

}



impl Default for ServiceRequestDetails_Response {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !rosapi_msgs__srv__ServiceRequestDetails_Response__init(&mut msg as *mut _) {
        panic!("Call to rosapi_msgs__srv__ServiceRequestDetails_Response__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for ServiceRequestDetails_Response {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__ServiceRequestDetails_Response__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__ServiceRequestDetails_Response__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__ServiceRequestDetails_Response__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for ServiceRequestDetails_Response {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for ServiceRequestDetails_Response where Self: Sized {
  const TYPE_NAME: &'static str = "rosapi_msgs/srv/ServiceRequestDetails_Response";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__rosapi_msgs__srv__ServiceRequestDetails_Response() }
  }
}


#[link(name = "rosapi_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__rosapi_msgs__srv__ServiceResponseDetails_Request() -> *const std::ffi::c_void;
}

#[link(name = "rosapi_msgs__rosidl_generator_c")]
extern "C" {
    fn rosapi_msgs__srv__ServiceResponseDetails_Request__init(msg: *mut ServiceResponseDetails_Request) -> bool;
    fn rosapi_msgs__srv__ServiceResponseDetails_Request__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<ServiceResponseDetails_Request>, size: usize) -> bool;
    fn rosapi_msgs__srv__ServiceResponseDetails_Request__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<ServiceResponseDetails_Request>);
    fn rosapi_msgs__srv__ServiceResponseDetails_Request__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<ServiceResponseDetails_Request>, out_seq: *mut rosidl_runtime_rs::Sequence<ServiceResponseDetails_Request>) -> bool;
}

// Corresponds to rosapi_msgs__srv__ServiceResponseDetails_Request
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct ServiceResponseDetails_Request {

    // This member is not documented.
    #[allow(missing_docs)]
    pub type_: rosidl_runtime_rs::String,

}



impl Default for ServiceResponseDetails_Request {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !rosapi_msgs__srv__ServiceResponseDetails_Request__init(&mut msg as *mut _) {
        panic!("Call to rosapi_msgs__srv__ServiceResponseDetails_Request__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for ServiceResponseDetails_Request {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__ServiceResponseDetails_Request__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__ServiceResponseDetails_Request__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__ServiceResponseDetails_Request__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for ServiceResponseDetails_Request {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for ServiceResponseDetails_Request where Self: Sized {
  const TYPE_NAME: &'static str = "rosapi_msgs/srv/ServiceResponseDetails_Request";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__rosapi_msgs__srv__ServiceResponseDetails_Request() }
  }
}


#[link(name = "rosapi_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__rosapi_msgs__srv__ServiceResponseDetails_Response() -> *const std::ffi::c_void;
}

#[link(name = "rosapi_msgs__rosidl_generator_c")]
extern "C" {
    fn rosapi_msgs__srv__ServiceResponseDetails_Response__init(msg: *mut ServiceResponseDetails_Response) -> bool;
    fn rosapi_msgs__srv__ServiceResponseDetails_Response__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<ServiceResponseDetails_Response>, size: usize) -> bool;
    fn rosapi_msgs__srv__ServiceResponseDetails_Response__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<ServiceResponseDetails_Response>);
    fn rosapi_msgs__srv__ServiceResponseDetails_Response__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<ServiceResponseDetails_Response>, out_seq: *mut rosidl_runtime_rs::Sequence<ServiceResponseDetails_Response>) -> bool;
}

// Corresponds to rosapi_msgs__srv__ServiceResponseDetails_Response
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct ServiceResponseDetails_Response {

    // This member is not documented.
    #[allow(missing_docs)]
    pub typedefs: rosidl_runtime_rs::Sequence<super::super::msg::rmw::TypeDef>,

}



impl Default for ServiceResponseDetails_Response {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !rosapi_msgs__srv__ServiceResponseDetails_Response__init(&mut msg as *mut _) {
        panic!("Call to rosapi_msgs__srv__ServiceResponseDetails_Response__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for ServiceResponseDetails_Response {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__ServiceResponseDetails_Response__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__ServiceResponseDetails_Response__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__ServiceResponseDetails_Response__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for ServiceResponseDetails_Response {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for ServiceResponseDetails_Response where Self: Sized {
  const TYPE_NAME: &'static str = "rosapi_msgs/srv/ServiceResponseDetails_Response";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__rosapi_msgs__srv__ServiceResponseDetails_Response() }
  }
}


#[link(name = "rosapi_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__rosapi_msgs__srv__Services_Request() -> *const std::ffi::c_void;
}

#[link(name = "rosapi_msgs__rosidl_generator_c")]
extern "C" {
    fn rosapi_msgs__srv__Services_Request__init(msg: *mut Services_Request) -> bool;
    fn rosapi_msgs__srv__Services_Request__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<Services_Request>, size: usize) -> bool;
    fn rosapi_msgs__srv__Services_Request__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<Services_Request>);
    fn rosapi_msgs__srv__Services_Request__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<Services_Request>, out_seq: *mut rosidl_runtime_rs::Sequence<Services_Request>) -> bool;
}

// Corresponds to rosapi_msgs__srv__Services_Request
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Services_Request {

    // This member is not documented.
    #[allow(missing_docs)]
    pub structure_needs_at_least_one_member: u8,

}



impl Default for Services_Request {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !rosapi_msgs__srv__Services_Request__init(&mut msg as *mut _) {
        panic!("Call to rosapi_msgs__srv__Services_Request__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for Services_Request {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__Services_Request__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__Services_Request__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__Services_Request__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for Services_Request {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for Services_Request where Self: Sized {
  const TYPE_NAME: &'static str = "rosapi_msgs/srv/Services_Request";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__rosapi_msgs__srv__Services_Request() }
  }
}


#[link(name = "rosapi_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__rosapi_msgs__srv__Services_Response() -> *const std::ffi::c_void;
}

#[link(name = "rosapi_msgs__rosidl_generator_c")]
extern "C" {
    fn rosapi_msgs__srv__Services_Response__init(msg: *mut Services_Response) -> bool;
    fn rosapi_msgs__srv__Services_Response__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<Services_Response>, size: usize) -> bool;
    fn rosapi_msgs__srv__Services_Response__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<Services_Response>);
    fn rosapi_msgs__srv__Services_Response__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<Services_Response>, out_seq: *mut rosidl_runtime_rs::Sequence<Services_Response>) -> bool;
}

// Corresponds to rosapi_msgs__srv__Services_Response
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Services_Response {

    // This member is not documented.
    #[allow(missing_docs)]
    pub services: rosidl_runtime_rs::Sequence<rosidl_runtime_rs::String>,

}



impl Default for Services_Response {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !rosapi_msgs__srv__Services_Response__init(&mut msg as *mut _) {
        panic!("Call to rosapi_msgs__srv__Services_Response__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for Services_Response {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__Services_Response__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__Services_Response__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__Services_Response__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for Services_Response {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for Services_Response where Self: Sized {
  const TYPE_NAME: &'static str = "rosapi_msgs/srv/Services_Response";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__rosapi_msgs__srv__Services_Response() }
  }
}


#[link(name = "rosapi_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__rosapi_msgs__srv__ServicesForType_Request() -> *const std::ffi::c_void;
}

#[link(name = "rosapi_msgs__rosidl_generator_c")]
extern "C" {
    fn rosapi_msgs__srv__ServicesForType_Request__init(msg: *mut ServicesForType_Request) -> bool;
    fn rosapi_msgs__srv__ServicesForType_Request__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<ServicesForType_Request>, size: usize) -> bool;
    fn rosapi_msgs__srv__ServicesForType_Request__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<ServicesForType_Request>);
    fn rosapi_msgs__srv__ServicesForType_Request__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<ServicesForType_Request>, out_seq: *mut rosidl_runtime_rs::Sequence<ServicesForType_Request>) -> bool;
}

// Corresponds to rosapi_msgs__srv__ServicesForType_Request
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct ServicesForType_Request {

    // This member is not documented.
    #[allow(missing_docs)]
    pub type_: rosidl_runtime_rs::String,

}



impl Default for ServicesForType_Request {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !rosapi_msgs__srv__ServicesForType_Request__init(&mut msg as *mut _) {
        panic!("Call to rosapi_msgs__srv__ServicesForType_Request__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for ServicesForType_Request {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__ServicesForType_Request__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__ServicesForType_Request__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__ServicesForType_Request__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for ServicesForType_Request {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for ServicesForType_Request where Self: Sized {
  const TYPE_NAME: &'static str = "rosapi_msgs/srv/ServicesForType_Request";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__rosapi_msgs__srv__ServicesForType_Request() }
  }
}


#[link(name = "rosapi_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__rosapi_msgs__srv__ServicesForType_Response() -> *const std::ffi::c_void;
}

#[link(name = "rosapi_msgs__rosidl_generator_c")]
extern "C" {
    fn rosapi_msgs__srv__ServicesForType_Response__init(msg: *mut ServicesForType_Response) -> bool;
    fn rosapi_msgs__srv__ServicesForType_Response__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<ServicesForType_Response>, size: usize) -> bool;
    fn rosapi_msgs__srv__ServicesForType_Response__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<ServicesForType_Response>);
    fn rosapi_msgs__srv__ServicesForType_Response__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<ServicesForType_Response>, out_seq: *mut rosidl_runtime_rs::Sequence<ServicesForType_Response>) -> bool;
}

// Corresponds to rosapi_msgs__srv__ServicesForType_Response
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct ServicesForType_Response {

    // This member is not documented.
    #[allow(missing_docs)]
    pub services: rosidl_runtime_rs::Sequence<rosidl_runtime_rs::String>,

}



impl Default for ServicesForType_Response {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !rosapi_msgs__srv__ServicesForType_Response__init(&mut msg as *mut _) {
        panic!("Call to rosapi_msgs__srv__ServicesForType_Response__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for ServicesForType_Response {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__ServicesForType_Response__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__ServicesForType_Response__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__ServicesForType_Response__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for ServicesForType_Response {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for ServicesForType_Response where Self: Sized {
  const TYPE_NAME: &'static str = "rosapi_msgs/srv/ServicesForType_Response";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__rosapi_msgs__srv__ServicesForType_Response() }
  }
}


#[link(name = "rosapi_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__rosapi_msgs__srv__ServiceType_Request() -> *const std::ffi::c_void;
}

#[link(name = "rosapi_msgs__rosidl_generator_c")]
extern "C" {
    fn rosapi_msgs__srv__ServiceType_Request__init(msg: *mut ServiceType_Request) -> bool;
    fn rosapi_msgs__srv__ServiceType_Request__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<ServiceType_Request>, size: usize) -> bool;
    fn rosapi_msgs__srv__ServiceType_Request__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<ServiceType_Request>);
    fn rosapi_msgs__srv__ServiceType_Request__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<ServiceType_Request>, out_seq: *mut rosidl_runtime_rs::Sequence<ServiceType_Request>) -> bool;
}

// Corresponds to rosapi_msgs__srv__ServiceType_Request
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct ServiceType_Request {

    // This member is not documented.
    #[allow(missing_docs)]
    pub service: rosidl_runtime_rs::String,

}



impl Default for ServiceType_Request {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !rosapi_msgs__srv__ServiceType_Request__init(&mut msg as *mut _) {
        panic!("Call to rosapi_msgs__srv__ServiceType_Request__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for ServiceType_Request {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__ServiceType_Request__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__ServiceType_Request__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__ServiceType_Request__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for ServiceType_Request {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for ServiceType_Request where Self: Sized {
  const TYPE_NAME: &'static str = "rosapi_msgs/srv/ServiceType_Request";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__rosapi_msgs__srv__ServiceType_Request() }
  }
}


#[link(name = "rosapi_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__rosapi_msgs__srv__ServiceType_Response() -> *const std::ffi::c_void;
}

#[link(name = "rosapi_msgs__rosidl_generator_c")]
extern "C" {
    fn rosapi_msgs__srv__ServiceType_Response__init(msg: *mut ServiceType_Response) -> bool;
    fn rosapi_msgs__srv__ServiceType_Response__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<ServiceType_Response>, size: usize) -> bool;
    fn rosapi_msgs__srv__ServiceType_Response__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<ServiceType_Response>);
    fn rosapi_msgs__srv__ServiceType_Response__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<ServiceType_Response>, out_seq: *mut rosidl_runtime_rs::Sequence<ServiceType_Response>) -> bool;
}

// Corresponds to rosapi_msgs__srv__ServiceType_Response
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct ServiceType_Response {

    // This member is not documented.
    #[allow(missing_docs)]
    pub type_: rosidl_runtime_rs::String,

}



impl Default for ServiceType_Response {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !rosapi_msgs__srv__ServiceType_Response__init(&mut msg as *mut _) {
        panic!("Call to rosapi_msgs__srv__ServiceType_Response__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for ServiceType_Response {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__ServiceType_Response__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__ServiceType_Response__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__ServiceType_Response__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for ServiceType_Response {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for ServiceType_Response where Self: Sized {
  const TYPE_NAME: &'static str = "rosapi_msgs/srv/ServiceType_Response";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__rosapi_msgs__srv__ServiceType_Response() }
  }
}


#[link(name = "rosapi_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__rosapi_msgs__srv__SetParam_Request() -> *const std::ffi::c_void;
}

#[link(name = "rosapi_msgs__rosidl_generator_c")]
extern "C" {
    fn rosapi_msgs__srv__SetParam_Request__init(msg: *mut SetParam_Request) -> bool;
    fn rosapi_msgs__srv__SetParam_Request__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<SetParam_Request>, size: usize) -> bool;
    fn rosapi_msgs__srv__SetParam_Request__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<SetParam_Request>);
    fn rosapi_msgs__srv__SetParam_Request__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<SetParam_Request>, out_seq: *mut rosidl_runtime_rs::Sequence<SetParam_Request>) -> bool;
}

// Corresponds to rosapi_msgs__srv__SetParam_Request
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct SetParam_Request {

    // This member is not documented.
    #[allow(missing_docs)]
    pub name: rosidl_runtime_rs::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub value: rosidl_runtime_rs::String,

}



impl Default for SetParam_Request {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !rosapi_msgs__srv__SetParam_Request__init(&mut msg as *mut _) {
        panic!("Call to rosapi_msgs__srv__SetParam_Request__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for SetParam_Request {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__SetParam_Request__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__SetParam_Request__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__SetParam_Request__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for SetParam_Request {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for SetParam_Request where Self: Sized {
  const TYPE_NAME: &'static str = "rosapi_msgs/srv/SetParam_Request";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__rosapi_msgs__srv__SetParam_Request() }
  }
}


#[link(name = "rosapi_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__rosapi_msgs__srv__SetParam_Response() -> *const std::ffi::c_void;
}

#[link(name = "rosapi_msgs__rosidl_generator_c")]
extern "C" {
    fn rosapi_msgs__srv__SetParam_Response__init(msg: *mut SetParam_Response) -> bool;
    fn rosapi_msgs__srv__SetParam_Response__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<SetParam_Response>, size: usize) -> bool;
    fn rosapi_msgs__srv__SetParam_Response__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<SetParam_Response>);
    fn rosapi_msgs__srv__SetParam_Response__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<SetParam_Response>, out_seq: *mut rosidl_runtime_rs::Sequence<SetParam_Response>) -> bool;
}

// Corresponds to rosapi_msgs__srv__SetParam_Response
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct SetParam_Response {

    // This member is not documented.
    #[allow(missing_docs)]
    pub structure_needs_at_least_one_member: u8,

}



impl Default for SetParam_Response {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !rosapi_msgs__srv__SetParam_Response__init(&mut msg as *mut _) {
        panic!("Call to rosapi_msgs__srv__SetParam_Response__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for SetParam_Response {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__SetParam_Response__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__SetParam_Response__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__SetParam_Response__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for SetParam_Response {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for SetParam_Response where Self: Sized {
  const TYPE_NAME: &'static str = "rosapi_msgs/srv/SetParam_Response";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__rosapi_msgs__srv__SetParam_Response() }
  }
}


#[link(name = "rosapi_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__rosapi_msgs__srv__Subscribers_Request() -> *const std::ffi::c_void;
}

#[link(name = "rosapi_msgs__rosidl_generator_c")]
extern "C" {
    fn rosapi_msgs__srv__Subscribers_Request__init(msg: *mut Subscribers_Request) -> bool;
    fn rosapi_msgs__srv__Subscribers_Request__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<Subscribers_Request>, size: usize) -> bool;
    fn rosapi_msgs__srv__Subscribers_Request__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<Subscribers_Request>);
    fn rosapi_msgs__srv__Subscribers_Request__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<Subscribers_Request>, out_seq: *mut rosidl_runtime_rs::Sequence<Subscribers_Request>) -> bool;
}

// Corresponds to rosapi_msgs__srv__Subscribers_Request
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Subscribers_Request {

    // This member is not documented.
    #[allow(missing_docs)]
    pub topic: rosidl_runtime_rs::String,

}



impl Default for Subscribers_Request {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !rosapi_msgs__srv__Subscribers_Request__init(&mut msg as *mut _) {
        panic!("Call to rosapi_msgs__srv__Subscribers_Request__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for Subscribers_Request {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__Subscribers_Request__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__Subscribers_Request__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__Subscribers_Request__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for Subscribers_Request {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for Subscribers_Request where Self: Sized {
  const TYPE_NAME: &'static str = "rosapi_msgs/srv/Subscribers_Request";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__rosapi_msgs__srv__Subscribers_Request() }
  }
}


#[link(name = "rosapi_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__rosapi_msgs__srv__Subscribers_Response() -> *const std::ffi::c_void;
}

#[link(name = "rosapi_msgs__rosidl_generator_c")]
extern "C" {
    fn rosapi_msgs__srv__Subscribers_Response__init(msg: *mut Subscribers_Response) -> bool;
    fn rosapi_msgs__srv__Subscribers_Response__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<Subscribers_Response>, size: usize) -> bool;
    fn rosapi_msgs__srv__Subscribers_Response__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<Subscribers_Response>);
    fn rosapi_msgs__srv__Subscribers_Response__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<Subscribers_Response>, out_seq: *mut rosidl_runtime_rs::Sequence<Subscribers_Response>) -> bool;
}

// Corresponds to rosapi_msgs__srv__Subscribers_Response
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Subscribers_Response {

    // This member is not documented.
    #[allow(missing_docs)]
    pub subscribers: rosidl_runtime_rs::Sequence<rosidl_runtime_rs::String>,

}



impl Default for Subscribers_Response {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !rosapi_msgs__srv__Subscribers_Response__init(&mut msg as *mut _) {
        panic!("Call to rosapi_msgs__srv__Subscribers_Response__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for Subscribers_Response {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__Subscribers_Response__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__Subscribers_Response__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__Subscribers_Response__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for Subscribers_Response {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for Subscribers_Response where Self: Sized {
  const TYPE_NAME: &'static str = "rosapi_msgs/srv/Subscribers_Response";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__rosapi_msgs__srv__Subscribers_Response() }
  }
}


#[link(name = "rosapi_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__rosapi_msgs__srv__Topics_Request() -> *const std::ffi::c_void;
}

#[link(name = "rosapi_msgs__rosidl_generator_c")]
extern "C" {
    fn rosapi_msgs__srv__Topics_Request__init(msg: *mut Topics_Request) -> bool;
    fn rosapi_msgs__srv__Topics_Request__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<Topics_Request>, size: usize) -> bool;
    fn rosapi_msgs__srv__Topics_Request__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<Topics_Request>);
    fn rosapi_msgs__srv__Topics_Request__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<Topics_Request>, out_seq: *mut rosidl_runtime_rs::Sequence<Topics_Request>) -> bool;
}

// Corresponds to rosapi_msgs__srv__Topics_Request
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Topics_Request {

    // This member is not documented.
    #[allow(missing_docs)]
    pub structure_needs_at_least_one_member: u8,

}



impl Default for Topics_Request {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !rosapi_msgs__srv__Topics_Request__init(&mut msg as *mut _) {
        panic!("Call to rosapi_msgs__srv__Topics_Request__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for Topics_Request {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__Topics_Request__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__Topics_Request__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__Topics_Request__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for Topics_Request {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for Topics_Request where Self: Sized {
  const TYPE_NAME: &'static str = "rosapi_msgs/srv/Topics_Request";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__rosapi_msgs__srv__Topics_Request() }
  }
}


#[link(name = "rosapi_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__rosapi_msgs__srv__Topics_Response() -> *const std::ffi::c_void;
}

#[link(name = "rosapi_msgs__rosidl_generator_c")]
extern "C" {
    fn rosapi_msgs__srv__Topics_Response__init(msg: *mut Topics_Response) -> bool;
    fn rosapi_msgs__srv__Topics_Response__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<Topics_Response>, size: usize) -> bool;
    fn rosapi_msgs__srv__Topics_Response__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<Topics_Response>);
    fn rosapi_msgs__srv__Topics_Response__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<Topics_Response>, out_seq: *mut rosidl_runtime_rs::Sequence<Topics_Response>) -> bool;
}

// Corresponds to rosapi_msgs__srv__Topics_Response
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Topics_Response {

    // This member is not documented.
    #[allow(missing_docs)]
    pub topics: rosidl_runtime_rs::Sequence<rosidl_runtime_rs::String>,


    // This member is not documented.
    #[allow(missing_docs)]
    pub types: rosidl_runtime_rs::Sequence<rosidl_runtime_rs::String>,

}



impl Default for Topics_Response {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !rosapi_msgs__srv__Topics_Response__init(&mut msg as *mut _) {
        panic!("Call to rosapi_msgs__srv__Topics_Response__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for Topics_Response {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__Topics_Response__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__Topics_Response__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__Topics_Response__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for Topics_Response {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for Topics_Response where Self: Sized {
  const TYPE_NAME: &'static str = "rosapi_msgs/srv/Topics_Response";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__rosapi_msgs__srv__Topics_Response() }
  }
}


#[link(name = "rosapi_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__rosapi_msgs__srv__TopicsAndRawTypes_Request() -> *const std::ffi::c_void;
}

#[link(name = "rosapi_msgs__rosidl_generator_c")]
extern "C" {
    fn rosapi_msgs__srv__TopicsAndRawTypes_Request__init(msg: *mut TopicsAndRawTypes_Request) -> bool;
    fn rosapi_msgs__srv__TopicsAndRawTypes_Request__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<TopicsAndRawTypes_Request>, size: usize) -> bool;
    fn rosapi_msgs__srv__TopicsAndRawTypes_Request__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<TopicsAndRawTypes_Request>);
    fn rosapi_msgs__srv__TopicsAndRawTypes_Request__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<TopicsAndRawTypes_Request>, out_seq: *mut rosidl_runtime_rs::Sequence<TopicsAndRawTypes_Request>) -> bool;
}

// Corresponds to rosapi_msgs__srv__TopicsAndRawTypes_Request
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct TopicsAndRawTypes_Request {

    // This member is not documented.
    #[allow(missing_docs)]
    pub structure_needs_at_least_one_member: u8,

}



impl Default for TopicsAndRawTypes_Request {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !rosapi_msgs__srv__TopicsAndRawTypes_Request__init(&mut msg as *mut _) {
        panic!("Call to rosapi_msgs__srv__TopicsAndRawTypes_Request__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for TopicsAndRawTypes_Request {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__TopicsAndRawTypes_Request__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__TopicsAndRawTypes_Request__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__TopicsAndRawTypes_Request__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for TopicsAndRawTypes_Request {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for TopicsAndRawTypes_Request where Self: Sized {
  const TYPE_NAME: &'static str = "rosapi_msgs/srv/TopicsAndRawTypes_Request";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__rosapi_msgs__srv__TopicsAndRawTypes_Request() }
  }
}


#[link(name = "rosapi_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__rosapi_msgs__srv__TopicsAndRawTypes_Response() -> *const std::ffi::c_void;
}

#[link(name = "rosapi_msgs__rosidl_generator_c")]
extern "C" {
    fn rosapi_msgs__srv__TopicsAndRawTypes_Response__init(msg: *mut TopicsAndRawTypes_Response) -> bool;
    fn rosapi_msgs__srv__TopicsAndRawTypes_Response__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<TopicsAndRawTypes_Response>, size: usize) -> bool;
    fn rosapi_msgs__srv__TopicsAndRawTypes_Response__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<TopicsAndRawTypes_Response>);
    fn rosapi_msgs__srv__TopicsAndRawTypes_Response__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<TopicsAndRawTypes_Response>, out_seq: *mut rosidl_runtime_rs::Sequence<TopicsAndRawTypes_Response>) -> bool;
}

// Corresponds to rosapi_msgs__srv__TopicsAndRawTypes_Response
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct TopicsAndRawTypes_Response {

    // This member is not documented.
    #[allow(missing_docs)]
    pub topics: rosidl_runtime_rs::Sequence<rosidl_runtime_rs::String>,


    // This member is not documented.
    #[allow(missing_docs)]
    pub types: rosidl_runtime_rs::Sequence<rosidl_runtime_rs::String>,


    // This member is not documented.
    #[allow(missing_docs)]
    pub typedefs_full_text: rosidl_runtime_rs::Sequence<rosidl_runtime_rs::String>,

}



impl Default for TopicsAndRawTypes_Response {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !rosapi_msgs__srv__TopicsAndRawTypes_Response__init(&mut msg as *mut _) {
        panic!("Call to rosapi_msgs__srv__TopicsAndRawTypes_Response__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for TopicsAndRawTypes_Response {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__TopicsAndRawTypes_Response__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__TopicsAndRawTypes_Response__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__TopicsAndRawTypes_Response__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for TopicsAndRawTypes_Response {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for TopicsAndRawTypes_Response where Self: Sized {
  const TYPE_NAME: &'static str = "rosapi_msgs/srv/TopicsAndRawTypes_Response";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__rosapi_msgs__srv__TopicsAndRawTypes_Response() }
  }
}


#[link(name = "rosapi_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__rosapi_msgs__srv__TopicsForType_Request() -> *const std::ffi::c_void;
}

#[link(name = "rosapi_msgs__rosidl_generator_c")]
extern "C" {
    fn rosapi_msgs__srv__TopicsForType_Request__init(msg: *mut TopicsForType_Request) -> bool;
    fn rosapi_msgs__srv__TopicsForType_Request__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<TopicsForType_Request>, size: usize) -> bool;
    fn rosapi_msgs__srv__TopicsForType_Request__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<TopicsForType_Request>);
    fn rosapi_msgs__srv__TopicsForType_Request__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<TopicsForType_Request>, out_seq: *mut rosidl_runtime_rs::Sequence<TopicsForType_Request>) -> bool;
}

// Corresponds to rosapi_msgs__srv__TopicsForType_Request
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct TopicsForType_Request {

    // This member is not documented.
    #[allow(missing_docs)]
    pub type_: rosidl_runtime_rs::String,

}



impl Default for TopicsForType_Request {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !rosapi_msgs__srv__TopicsForType_Request__init(&mut msg as *mut _) {
        panic!("Call to rosapi_msgs__srv__TopicsForType_Request__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for TopicsForType_Request {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__TopicsForType_Request__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__TopicsForType_Request__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__TopicsForType_Request__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for TopicsForType_Request {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for TopicsForType_Request where Self: Sized {
  const TYPE_NAME: &'static str = "rosapi_msgs/srv/TopicsForType_Request";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__rosapi_msgs__srv__TopicsForType_Request() }
  }
}


#[link(name = "rosapi_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__rosapi_msgs__srv__TopicsForType_Response() -> *const std::ffi::c_void;
}

#[link(name = "rosapi_msgs__rosidl_generator_c")]
extern "C" {
    fn rosapi_msgs__srv__TopicsForType_Response__init(msg: *mut TopicsForType_Response) -> bool;
    fn rosapi_msgs__srv__TopicsForType_Response__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<TopicsForType_Response>, size: usize) -> bool;
    fn rosapi_msgs__srv__TopicsForType_Response__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<TopicsForType_Response>);
    fn rosapi_msgs__srv__TopicsForType_Response__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<TopicsForType_Response>, out_seq: *mut rosidl_runtime_rs::Sequence<TopicsForType_Response>) -> bool;
}

// Corresponds to rosapi_msgs__srv__TopicsForType_Response
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct TopicsForType_Response {

    // This member is not documented.
    #[allow(missing_docs)]
    pub topics: rosidl_runtime_rs::Sequence<rosidl_runtime_rs::String>,

}



impl Default for TopicsForType_Response {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !rosapi_msgs__srv__TopicsForType_Response__init(&mut msg as *mut _) {
        panic!("Call to rosapi_msgs__srv__TopicsForType_Response__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for TopicsForType_Response {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__TopicsForType_Response__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__TopicsForType_Response__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__TopicsForType_Response__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for TopicsForType_Response {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for TopicsForType_Response where Self: Sized {
  const TYPE_NAME: &'static str = "rosapi_msgs/srv/TopicsForType_Response";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__rosapi_msgs__srv__TopicsForType_Response() }
  }
}


#[link(name = "rosapi_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__rosapi_msgs__srv__TopicType_Request() -> *const std::ffi::c_void;
}

#[link(name = "rosapi_msgs__rosidl_generator_c")]
extern "C" {
    fn rosapi_msgs__srv__TopicType_Request__init(msg: *mut TopicType_Request) -> bool;
    fn rosapi_msgs__srv__TopicType_Request__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<TopicType_Request>, size: usize) -> bool;
    fn rosapi_msgs__srv__TopicType_Request__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<TopicType_Request>);
    fn rosapi_msgs__srv__TopicType_Request__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<TopicType_Request>, out_seq: *mut rosidl_runtime_rs::Sequence<TopicType_Request>) -> bool;
}

// Corresponds to rosapi_msgs__srv__TopicType_Request
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct TopicType_Request {

    // This member is not documented.
    #[allow(missing_docs)]
    pub topic: rosidl_runtime_rs::String,

}



impl Default for TopicType_Request {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !rosapi_msgs__srv__TopicType_Request__init(&mut msg as *mut _) {
        panic!("Call to rosapi_msgs__srv__TopicType_Request__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for TopicType_Request {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__TopicType_Request__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__TopicType_Request__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__TopicType_Request__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for TopicType_Request {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for TopicType_Request where Self: Sized {
  const TYPE_NAME: &'static str = "rosapi_msgs/srv/TopicType_Request";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__rosapi_msgs__srv__TopicType_Request() }
  }
}


#[link(name = "rosapi_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__rosapi_msgs__srv__TopicType_Response() -> *const std::ffi::c_void;
}

#[link(name = "rosapi_msgs__rosidl_generator_c")]
extern "C" {
    fn rosapi_msgs__srv__TopicType_Response__init(msg: *mut TopicType_Response) -> bool;
    fn rosapi_msgs__srv__TopicType_Response__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<TopicType_Response>, size: usize) -> bool;
    fn rosapi_msgs__srv__TopicType_Response__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<TopicType_Response>);
    fn rosapi_msgs__srv__TopicType_Response__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<TopicType_Response>, out_seq: *mut rosidl_runtime_rs::Sequence<TopicType_Response>) -> bool;
}

// Corresponds to rosapi_msgs__srv__TopicType_Response
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct TopicType_Response {

    // This member is not documented.
    #[allow(missing_docs)]
    pub type_: rosidl_runtime_rs::String,

}



impl Default for TopicType_Response {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !rosapi_msgs__srv__TopicType_Response__init(&mut msg as *mut _) {
        panic!("Call to rosapi_msgs__srv__TopicType_Response__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for TopicType_Response {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__TopicType_Response__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__TopicType_Response__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rosapi_msgs__srv__TopicType_Response__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for TopicType_Response {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for TopicType_Response where Self: Sized {
  const TYPE_NAME: &'static str = "rosapi_msgs/srv/TopicType_Response";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__rosapi_msgs__srv__TopicType_Response() }
  }
}






#[link(name = "rosapi_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_service_type_support_handle__rosapi_msgs__srv__DeleteParam() -> *const std::ffi::c_void;
}

// Corresponds to rosapi_msgs__srv__DeleteParam
#[allow(missing_docs, non_camel_case_types)]
pub struct DeleteParam;

impl rosidl_runtime_rs::Service for DeleteParam {
    type Request = DeleteParam_Request;
    type Response = DeleteParam_Response;

    fn get_type_support() -> *const std::ffi::c_void {
        // SAFETY: No preconditions for this function.
        unsafe { rosidl_typesupport_c__get_service_type_support_handle__rosapi_msgs__srv__DeleteParam() }
    }
}




#[link(name = "rosapi_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_service_type_support_handle__rosapi_msgs__srv__GetActionServers() -> *const std::ffi::c_void;
}

// Corresponds to rosapi_msgs__srv__GetActionServers
#[allow(missing_docs, non_camel_case_types)]
pub struct GetActionServers;

impl rosidl_runtime_rs::Service for GetActionServers {
    type Request = GetActionServers_Request;
    type Response = GetActionServers_Response;

    fn get_type_support() -> *const std::ffi::c_void {
        // SAFETY: No preconditions for this function.
        unsafe { rosidl_typesupport_c__get_service_type_support_handle__rosapi_msgs__srv__GetActionServers() }
    }
}




#[link(name = "rosapi_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_service_type_support_handle__rosapi_msgs__srv__GetParam() -> *const std::ffi::c_void;
}

// Corresponds to rosapi_msgs__srv__GetParam
#[allow(missing_docs, non_camel_case_types)]
pub struct GetParam;

impl rosidl_runtime_rs::Service for GetParam {
    type Request = GetParam_Request;
    type Response = GetParam_Response;

    fn get_type_support() -> *const std::ffi::c_void {
        // SAFETY: No preconditions for this function.
        unsafe { rosidl_typesupport_c__get_service_type_support_handle__rosapi_msgs__srv__GetParam() }
    }
}




#[link(name = "rosapi_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_service_type_support_handle__rosapi_msgs__srv__GetParamNames() -> *const std::ffi::c_void;
}

// Corresponds to rosapi_msgs__srv__GetParamNames
#[allow(missing_docs, non_camel_case_types)]
pub struct GetParamNames;

impl rosidl_runtime_rs::Service for GetParamNames {
    type Request = GetParamNames_Request;
    type Response = GetParamNames_Response;

    fn get_type_support() -> *const std::ffi::c_void {
        // SAFETY: No preconditions for this function.
        unsafe { rosidl_typesupport_c__get_service_type_support_handle__rosapi_msgs__srv__GetParamNames() }
    }
}




#[link(name = "rosapi_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_service_type_support_handle__rosapi_msgs__srv__GetROSVersion() -> *const std::ffi::c_void;
}

// Corresponds to rosapi_msgs__srv__GetROSVersion
#[allow(missing_docs, non_camel_case_types)]
pub struct GetROSVersion;

impl rosidl_runtime_rs::Service for GetROSVersion {
    type Request = GetROSVersion_Request;
    type Response = GetROSVersion_Response;

    fn get_type_support() -> *const std::ffi::c_void {
        // SAFETY: No preconditions for this function.
        unsafe { rosidl_typesupport_c__get_service_type_support_handle__rosapi_msgs__srv__GetROSVersion() }
    }
}




#[link(name = "rosapi_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_service_type_support_handle__rosapi_msgs__srv__GetTime() -> *const std::ffi::c_void;
}

// Corresponds to rosapi_msgs__srv__GetTime
#[allow(missing_docs, non_camel_case_types)]
pub struct GetTime;

impl rosidl_runtime_rs::Service for GetTime {
    type Request = GetTime_Request;
    type Response = GetTime_Response;

    fn get_type_support() -> *const std::ffi::c_void {
        // SAFETY: No preconditions for this function.
        unsafe { rosidl_typesupport_c__get_service_type_support_handle__rosapi_msgs__srv__GetTime() }
    }
}




#[link(name = "rosapi_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_service_type_support_handle__rosapi_msgs__srv__HasParam() -> *const std::ffi::c_void;
}

// Corresponds to rosapi_msgs__srv__HasParam
#[allow(missing_docs, non_camel_case_types)]
pub struct HasParam;

impl rosidl_runtime_rs::Service for HasParam {
    type Request = HasParam_Request;
    type Response = HasParam_Response;

    fn get_type_support() -> *const std::ffi::c_void {
        // SAFETY: No preconditions for this function.
        unsafe { rosidl_typesupport_c__get_service_type_support_handle__rosapi_msgs__srv__HasParam() }
    }
}




#[link(name = "rosapi_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_service_type_support_handle__rosapi_msgs__srv__MessageDetails() -> *const std::ffi::c_void;
}

// Corresponds to rosapi_msgs__srv__MessageDetails
#[allow(missing_docs, non_camel_case_types)]
pub struct MessageDetails;

impl rosidl_runtime_rs::Service for MessageDetails {
    type Request = MessageDetails_Request;
    type Response = MessageDetails_Response;

    fn get_type_support() -> *const std::ffi::c_void {
        // SAFETY: No preconditions for this function.
        unsafe { rosidl_typesupport_c__get_service_type_support_handle__rosapi_msgs__srv__MessageDetails() }
    }
}




#[link(name = "rosapi_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_service_type_support_handle__rosapi_msgs__srv__Nodes() -> *const std::ffi::c_void;
}

// Corresponds to rosapi_msgs__srv__Nodes
#[allow(missing_docs, non_camel_case_types)]
pub struct Nodes;

impl rosidl_runtime_rs::Service for Nodes {
    type Request = Nodes_Request;
    type Response = Nodes_Response;

    fn get_type_support() -> *const std::ffi::c_void {
        // SAFETY: No preconditions for this function.
        unsafe { rosidl_typesupport_c__get_service_type_support_handle__rosapi_msgs__srv__Nodes() }
    }
}




#[link(name = "rosapi_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_service_type_support_handle__rosapi_msgs__srv__NodeDetails() -> *const std::ffi::c_void;
}

// Corresponds to rosapi_msgs__srv__NodeDetails
#[allow(missing_docs, non_camel_case_types)]
pub struct NodeDetails;

impl rosidl_runtime_rs::Service for NodeDetails {
    type Request = NodeDetails_Request;
    type Response = NodeDetails_Response;

    fn get_type_support() -> *const std::ffi::c_void {
        // SAFETY: No preconditions for this function.
        unsafe { rosidl_typesupport_c__get_service_type_support_handle__rosapi_msgs__srv__NodeDetails() }
    }
}




#[link(name = "rosapi_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_service_type_support_handle__rosapi_msgs__srv__Publishers() -> *const std::ffi::c_void;
}

// Corresponds to rosapi_msgs__srv__Publishers
#[allow(missing_docs, non_camel_case_types)]
pub struct Publishers;

impl rosidl_runtime_rs::Service for Publishers {
    type Request = Publishers_Request;
    type Response = Publishers_Response;

    fn get_type_support() -> *const std::ffi::c_void {
        // SAFETY: No preconditions for this function.
        unsafe { rosidl_typesupport_c__get_service_type_support_handle__rosapi_msgs__srv__Publishers() }
    }
}




#[link(name = "rosapi_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_service_type_support_handle__rosapi_msgs__srv__ServiceNode() -> *const std::ffi::c_void;
}

// Corresponds to rosapi_msgs__srv__ServiceNode
#[allow(missing_docs, non_camel_case_types)]
pub struct ServiceNode;

impl rosidl_runtime_rs::Service for ServiceNode {
    type Request = ServiceNode_Request;
    type Response = ServiceNode_Response;

    fn get_type_support() -> *const std::ffi::c_void {
        // SAFETY: No preconditions for this function.
        unsafe { rosidl_typesupport_c__get_service_type_support_handle__rosapi_msgs__srv__ServiceNode() }
    }
}




#[link(name = "rosapi_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_service_type_support_handle__rosapi_msgs__srv__ServiceProviders() -> *const std::ffi::c_void;
}

// Corresponds to rosapi_msgs__srv__ServiceProviders
#[allow(missing_docs, non_camel_case_types)]
pub struct ServiceProviders;

impl rosidl_runtime_rs::Service for ServiceProviders {
    type Request = ServiceProviders_Request;
    type Response = ServiceProviders_Response;

    fn get_type_support() -> *const std::ffi::c_void {
        // SAFETY: No preconditions for this function.
        unsafe { rosidl_typesupport_c__get_service_type_support_handle__rosapi_msgs__srv__ServiceProviders() }
    }
}




#[link(name = "rosapi_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_service_type_support_handle__rosapi_msgs__srv__ServiceRequestDetails() -> *const std::ffi::c_void;
}

// Corresponds to rosapi_msgs__srv__ServiceRequestDetails
#[allow(missing_docs, non_camel_case_types)]
pub struct ServiceRequestDetails;

impl rosidl_runtime_rs::Service for ServiceRequestDetails {
    type Request = ServiceRequestDetails_Request;
    type Response = ServiceRequestDetails_Response;

    fn get_type_support() -> *const std::ffi::c_void {
        // SAFETY: No preconditions for this function.
        unsafe { rosidl_typesupport_c__get_service_type_support_handle__rosapi_msgs__srv__ServiceRequestDetails() }
    }
}




#[link(name = "rosapi_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_service_type_support_handle__rosapi_msgs__srv__ServiceResponseDetails() -> *const std::ffi::c_void;
}

// Corresponds to rosapi_msgs__srv__ServiceResponseDetails
#[allow(missing_docs, non_camel_case_types)]
pub struct ServiceResponseDetails;

impl rosidl_runtime_rs::Service for ServiceResponseDetails {
    type Request = ServiceResponseDetails_Request;
    type Response = ServiceResponseDetails_Response;

    fn get_type_support() -> *const std::ffi::c_void {
        // SAFETY: No preconditions for this function.
        unsafe { rosidl_typesupport_c__get_service_type_support_handle__rosapi_msgs__srv__ServiceResponseDetails() }
    }
}




#[link(name = "rosapi_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_service_type_support_handle__rosapi_msgs__srv__Services() -> *const std::ffi::c_void;
}

// Corresponds to rosapi_msgs__srv__Services
#[allow(missing_docs, non_camel_case_types)]
pub struct Services;

impl rosidl_runtime_rs::Service for Services {
    type Request = Services_Request;
    type Response = Services_Response;

    fn get_type_support() -> *const std::ffi::c_void {
        // SAFETY: No preconditions for this function.
        unsafe { rosidl_typesupport_c__get_service_type_support_handle__rosapi_msgs__srv__Services() }
    }
}




#[link(name = "rosapi_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_service_type_support_handle__rosapi_msgs__srv__ServicesForType() -> *const std::ffi::c_void;
}

// Corresponds to rosapi_msgs__srv__ServicesForType
#[allow(missing_docs, non_camel_case_types)]
pub struct ServicesForType;

impl rosidl_runtime_rs::Service for ServicesForType {
    type Request = ServicesForType_Request;
    type Response = ServicesForType_Response;

    fn get_type_support() -> *const std::ffi::c_void {
        // SAFETY: No preconditions for this function.
        unsafe { rosidl_typesupport_c__get_service_type_support_handle__rosapi_msgs__srv__ServicesForType() }
    }
}




#[link(name = "rosapi_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_service_type_support_handle__rosapi_msgs__srv__ServiceType() -> *const std::ffi::c_void;
}

// Corresponds to rosapi_msgs__srv__ServiceType
#[allow(missing_docs, non_camel_case_types)]
pub struct ServiceType;

impl rosidl_runtime_rs::Service for ServiceType {
    type Request = ServiceType_Request;
    type Response = ServiceType_Response;

    fn get_type_support() -> *const std::ffi::c_void {
        // SAFETY: No preconditions for this function.
        unsafe { rosidl_typesupport_c__get_service_type_support_handle__rosapi_msgs__srv__ServiceType() }
    }
}




#[link(name = "rosapi_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_service_type_support_handle__rosapi_msgs__srv__SetParam() -> *const std::ffi::c_void;
}

// Corresponds to rosapi_msgs__srv__SetParam
#[allow(missing_docs, non_camel_case_types)]
pub struct SetParam;

impl rosidl_runtime_rs::Service for SetParam {
    type Request = SetParam_Request;
    type Response = SetParam_Response;

    fn get_type_support() -> *const std::ffi::c_void {
        // SAFETY: No preconditions for this function.
        unsafe { rosidl_typesupport_c__get_service_type_support_handle__rosapi_msgs__srv__SetParam() }
    }
}




#[link(name = "rosapi_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_service_type_support_handle__rosapi_msgs__srv__Subscribers() -> *const std::ffi::c_void;
}

// Corresponds to rosapi_msgs__srv__Subscribers
#[allow(missing_docs, non_camel_case_types)]
pub struct Subscribers;

impl rosidl_runtime_rs::Service for Subscribers {
    type Request = Subscribers_Request;
    type Response = Subscribers_Response;

    fn get_type_support() -> *const std::ffi::c_void {
        // SAFETY: No preconditions for this function.
        unsafe { rosidl_typesupport_c__get_service_type_support_handle__rosapi_msgs__srv__Subscribers() }
    }
}




#[link(name = "rosapi_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_service_type_support_handle__rosapi_msgs__srv__Topics() -> *const std::ffi::c_void;
}

// Corresponds to rosapi_msgs__srv__Topics
#[allow(missing_docs, non_camel_case_types)]
pub struct Topics;

impl rosidl_runtime_rs::Service for Topics {
    type Request = Topics_Request;
    type Response = Topics_Response;

    fn get_type_support() -> *const std::ffi::c_void {
        // SAFETY: No preconditions for this function.
        unsafe { rosidl_typesupport_c__get_service_type_support_handle__rosapi_msgs__srv__Topics() }
    }
}




#[link(name = "rosapi_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_service_type_support_handle__rosapi_msgs__srv__TopicsAndRawTypes() -> *const std::ffi::c_void;
}

// Corresponds to rosapi_msgs__srv__TopicsAndRawTypes
#[allow(missing_docs, non_camel_case_types)]
pub struct TopicsAndRawTypes;

impl rosidl_runtime_rs::Service for TopicsAndRawTypes {
    type Request = TopicsAndRawTypes_Request;
    type Response = TopicsAndRawTypes_Response;

    fn get_type_support() -> *const std::ffi::c_void {
        // SAFETY: No preconditions for this function.
        unsafe { rosidl_typesupport_c__get_service_type_support_handle__rosapi_msgs__srv__TopicsAndRawTypes() }
    }
}




#[link(name = "rosapi_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_service_type_support_handle__rosapi_msgs__srv__TopicsForType() -> *const std::ffi::c_void;
}

// Corresponds to rosapi_msgs__srv__TopicsForType
#[allow(missing_docs, non_camel_case_types)]
pub struct TopicsForType;

impl rosidl_runtime_rs::Service for TopicsForType {
    type Request = TopicsForType_Request;
    type Response = TopicsForType_Response;

    fn get_type_support() -> *const std::ffi::c_void {
        // SAFETY: No preconditions for this function.
        unsafe { rosidl_typesupport_c__get_service_type_support_handle__rosapi_msgs__srv__TopicsForType() }
    }
}




#[link(name = "rosapi_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_service_type_support_handle__rosapi_msgs__srv__TopicType() -> *const std::ffi::c_void;
}

// Corresponds to rosapi_msgs__srv__TopicType
#[allow(missing_docs, non_camel_case_types)]
pub struct TopicType;

impl rosidl_runtime_rs::Service for TopicType {
    type Request = TopicType_Request;
    type Response = TopicType_Response;

    fn get_type_support() -> *const std::ffi::c_void {
        // SAFETY: No preconditions for this function.
        unsafe { rosidl_typesupport_c__get_service_type_support_handle__rosapi_msgs__srv__TopicType() }
    }
}


