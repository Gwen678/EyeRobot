#[cfg(feature = "serde")]
use serde::{Deserialize, Serialize};




// Corresponds to rosapi_msgs__srv__DeleteParam_Request

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct DeleteParam_Request {

    // This member is not documented.
    #[allow(missing_docs)]
    pub name: std::string::String,

}



impl Default for DeleteParam_Request {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::srv::rmw::DeleteParam_Request::default())
  }
}

impl rosidl_runtime_rs::Message for DeleteParam_Request {
  type RmwMsg = super::srv::rmw::DeleteParam_Request;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        name: msg.name.as_str().into(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        name: msg.name.as_str().into(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      name: msg.name.to_string(),
    }
  }
}


// Corresponds to rosapi_msgs__srv__DeleteParam_Response

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct DeleteParam_Response {

    // This member is not documented.
    #[allow(missing_docs)]
    pub structure_needs_at_least_one_member: u8,

}



impl Default for DeleteParam_Response {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::srv::rmw::DeleteParam_Response::default())
  }
}

impl rosidl_runtime_rs::Message for DeleteParam_Response {
  type RmwMsg = super::srv::rmw::DeleteParam_Response;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        structure_needs_at_least_one_member: msg.structure_needs_at_least_one_member,
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
      structure_needs_at_least_one_member: msg.structure_needs_at_least_one_member,
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      structure_needs_at_least_one_member: msg.structure_needs_at_least_one_member,
    }
  }
}


// Corresponds to rosapi_msgs__srv__GetActionServers_Request

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct GetActionServers_Request {

    // This member is not documented.
    #[allow(missing_docs)]
    pub structure_needs_at_least_one_member: u8,

}



impl Default for GetActionServers_Request {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::srv::rmw::GetActionServers_Request::default())
  }
}

impl rosidl_runtime_rs::Message for GetActionServers_Request {
  type RmwMsg = super::srv::rmw::GetActionServers_Request;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        structure_needs_at_least_one_member: msg.structure_needs_at_least_one_member,
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
      structure_needs_at_least_one_member: msg.structure_needs_at_least_one_member,
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      structure_needs_at_least_one_member: msg.structure_needs_at_least_one_member,
    }
  }
}


// Corresponds to rosapi_msgs__srv__GetActionServers_Response

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct GetActionServers_Response {

    // This member is not documented.
    #[allow(missing_docs)]
    pub action_servers: Vec<std::string::String>,

}



impl Default for GetActionServers_Response {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::srv::rmw::GetActionServers_Response::default())
  }
}

impl rosidl_runtime_rs::Message for GetActionServers_Response {
  type RmwMsg = super::srv::rmw::GetActionServers_Response;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        action_servers: msg.action_servers
          .into_iter()
          .map(|elem| elem.as_str().into())
          .collect(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        action_servers: msg.action_servers
          .iter()
          .map(|elem| elem.as_str().into())
          .collect(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      action_servers: msg.action_servers
          .into_iter()
          .map(|elem| elem.to_string())
          .collect(),
    }
  }
}


// Corresponds to rosapi_msgs__srv__GetParam_Request

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct GetParam_Request {

    // This member is not documented.
    #[allow(missing_docs)]
    pub name: std::string::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub default_value: std::string::String,

}



impl Default for GetParam_Request {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::srv::rmw::GetParam_Request::default())
  }
}

impl rosidl_runtime_rs::Message for GetParam_Request {
  type RmwMsg = super::srv::rmw::GetParam_Request;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        name: msg.name.as_str().into(),
        default_value: msg.default_value.as_str().into(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        name: msg.name.as_str().into(),
        default_value: msg.default_value.as_str().into(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      name: msg.name.to_string(),
      default_value: msg.default_value.to_string(),
    }
  }
}


// Corresponds to rosapi_msgs__srv__GetParam_Response

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct GetParam_Response {

    // This member is not documented.
    #[allow(missing_docs)]
    pub value: std::string::String,

}



impl Default for GetParam_Response {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::srv::rmw::GetParam_Response::default())
  }
}

impl rosidl_runtime_rs::Message for GetParam_Response {
  type RmwMsg = super::srv::rmw::GetParam_Response;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        value: msg.value.as_str().into(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        value: msg.value.as_str().into(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      value: msg.value.to_string(),
    }
  }
}


// Corresponds to rosapi_msgs__srv__GetParamNames_Request

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct GetParamNames_Request {

    // This member is not documented.
    #[allow(missing_docs)]
    pub structure_needs_at_least_one_member: u8,

}



impl Default for GetParamNames_Request {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::srv::rmw::GetParamNames_Request::default())
  }
}

impl rosidl_runtime_rs::Message for GetParamNames_Request {
  type RmwMsg = super::srv::rmw::GetParamNames_Request;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        structure_needs_at_least_one_member: msg.structure_needs_at_least_one_member,
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
      structure_needs_at_least_one_member: msg.structure_needs_at_least_one_member,
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      structure_needs_at_least_one_member: msg.structure_needs_at_least_one_member,
    }
  }
}


// Corresponds to rosapi_msgs__srv__GetParamNames_Response

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct GetParamNames_Response {

    // This member is not documented.
    #[allow(missing_docs)]
    pub names: Vec<std::string::String>,

}



impl Default for GetParamNames_Response {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::srv::rmw::GetParamNames_Response::default())
  }
}

impl rosidl_runtime_rs::Message for GetParamNames_Response {
  type RmwMsg = super::srv::rmw::GetParamNames_Response;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        names: msg.names
          .into_iter()
          .map(|elem| elem.as_str().into())
          .collect(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        names: msg.names
          .iter()
          .map(|elem| elem.as_str().into())
          .collect(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      names: msg.names
          .into_iter()
          .map(|elem| elem.to_string())
          .collect(),
    }
  }
}


// Corresponds to rosapi_msgs__srv__GetROSVersion_Request

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct GetROSVersion_Request {

    // This member is not documented.
    #[allow(missing_docs)]
    pub structure_needs_at_least_one_member: u8,

}



impl Default for GetROSVersion_Request {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::srv::rmw::GetROSVersion_Request::default())
  }
}

impl rosidl_runtime_rs::Message for GetROSVersion_Request {
  type RmwMsg = super::srv::rmw::GetROSVersion_Request;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        structure_needs_at_least_one_member: msg.structure_needs_at_least_one_member,
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
      structure_needs_at_least_one_member: msg.structure_needs_at_least_one_member,
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      structure_needs_at_least_one_member: msg.structure_needs_at_least_one_member,
    }
  }
}


// Corresponds to rosapi_msgs__srv__GetROSVersion_Response

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct GetROSVersion_Response {

    // This member is not documented.
    #[allow(missing_docs)]
    pub version: u8,


    // This member is not documented.
    #[allow(missing_docs)]
    pub distro: std::string::String,

}



impl Default for GetROSVersion_Response {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::srv::rmw::GetROSVersion_Response::default())
  }
}

impl rosidl_runtime_rs::Message for GetROSVersion_Response {
  type RmwMsg = super::srv::rmw::GetROSVersion_Response;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        version: msg.version,
        distro: msg.distro.as_str().into(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
      version: msg.version,
        distro: msg.distro.as_str().into(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      version: msg.version,
      distro: msg.distro.to_string(),
    }
  }
}


// Corresponds to rosapi_msgs__srv__GetTime_Request

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct GetTime_Request {

    // This member is not documented.
    #[allow(missing_docs)]
    pub structure_needs_at_least_one_member: u8,

}



impl Default for GetTime_Request {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::srv::rmw::GetTime_Request::default())
  }
}

impl rosidl_runtime_rs::Message for GetTime_Request {
  type RmwMsg = super::srv::rmw::GetTime_Request;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        structure_needs_at_least_one_member: msg.structure_needs_at_least_one_member,
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
      structure_needs_at_least_one_member: msg.structure_needs_at_least_one_member,
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      structure_needs_at_least_one_member: msg.structure_needs_at_least_one_member,
    }
  }
}


// Corresponds to rosapi_msgs__srv__GetTime_Response

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct GetTime_Response {

    // This member is not documented.
    #[allow(missing_docs)]
    pub time: builtin_interfaces::msg::Time,

}



impl Default for GetTime_Response {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::srv::rmw::GetTime_Response::default())
  }
}

impl rosidl_runtime_rs::Message for GetTime_Response {
  type RmwMsg = super::srv::rmw::GetTime_Response;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        time: builtin_interfaces::msg::Time::into_rmw_message(std::borrow::Cow::Owned(msg.time)).into_owned(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        time: builtin_interfaces::msg::Time::into_rmw_message(std::borrow::Cow::Borrowed(&msg.time)).into_owned(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      time: builtin_interfaces::msg::Time::from_rmw_message(msg.time),
    }
  }
}


// Corresponds to rosapi_msgs__srv__HasParam_Request

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct HasParam_Request {

    // This member is not documented.
    #[allow(missing_docs)]
    pub name: std::string::String,

}



impl Default for HasParam_Request {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::srv::rmw::HasParam_Request::default())
  }
}

impl rosidl_runtime_rs::Message for HasParam_Request {
  type RmwMsg = super::srv::rmw::HasParam_Request;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        name: msg.name.as_str().into(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        name: msg.name.as_str().into(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      name: msg.name.to_string(),
    }
  }
}


// Corresponds to rosapi_msgs__srv__HasParam_Response

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct HasParam_Response {

    // This member is not documented.
    #[allow(missing_docs)]
    pub exists: bool,

}



impl Default for HasParam_Response {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::srv::rmw::HasParam_Response::default())
  }
}

impl rosidl_runtime_rs::Message for HasParam_Response {
  type RmwMsg = super::srv::rmw::HasParam_Response;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        exists: msg.exists,
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
      exists: msg.exists,
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      exists: msg.exists,
    }
  }
}


// Corresponds to rosapi_msgs__srv__MessageDetails_Request

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct MessageDetails_Request {

    // This member is not documented.
    #[allow(missing_docs)]
    pub type_: std::string::String,

}



impl Default for MessageDetails_Request {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::srv::rmw::MessageDetails_Request::default())
  }
}

impl rosidl_runtime_rs::Message for MessageDetails_Request {
  type RmwMsg = super::srv::rmw::MessageDetails_Request;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        type_: msg.type_.as_str().into(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        type_: msg.type_.as_str().into(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      type_: msg.type_.to_string(),
    }
  }
}


// Corresponds to rosapi_msgs__srv__MessageDetails_Response

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct MessageDetails_Response {

    // This member is not documented.
    #[allow(missing_docs)]
    pub typedefs: Vec<super::msg::TypeDef>,

}



impl Default for MessageDetails_Response {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::srv::rmw::MessageDetails_Response::default())
  }
}

impl rosidl_runtime_rs::Message for MessageDetails_Response {
  type RmwMsg = super::srv::rmw::MessageDetails_Response;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        typedefs: msg.typedefs
          .into_iter()
          .map(|elem| super::msg::TypeDef::into_rmw_message(std::borrow::Cow::Owned(elem)).into_owned())
          .collect(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        typedefs: msg.typedefs
          .iter()
          .map(|elem| super::msg::TypeDef::into_rmw_message(std::borrow::Cow::Borrowed(elem)).into_owned())
          .collect(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      typedefs: msg.typedefs
          .into_iter()
          .map(super::msg::TypeDef::from_rmw_message)
          .collect(),
    }
  }
}


// Corresponds to rosapi_msgs__srv__Nodes_Request

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Nodes_Request {

    // This member is not documented.
    #[allow(missing_docs)]
    pub structure_needs_at_least_one_member: u8,

}



impl Default for Nodes_Request {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::srv::rmw::Nodes_Request::default())
  }
}

impl rosidl_runtime_rs::Message for Nodes_Request {
  type RmwMsg = super::srv::rmw::Nodes_Request;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        structure_needs_at_least_one_member: msg.structure_needs_at_least_one_member,
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
      structure_needs_at_least_one_member: msg.structure_needs_at_least_one_member,
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      structure_needs_at_least_one_member: msg.structure_needs_at_least_one_member,
    }
  }
}


// Corresponds to rosapi_msgs__srv__Nodes_Response

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Nodes_Response {

    // This member is not documented.
    #[allow(missing_docs)]
    pub nodes: Vec<std::string::String>,

}



impl Default for Nodes_Response {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::srv::rmw::Nodes_Response::default())
  }
}

impl rosidl_runtime_rs::Message for Nodes_Response {
  type RmwMsg = super::srv::rmw::Nodes_Response;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        nodes: msg.nodes
          .into_iter()
          .map(|elem| elem.as_str().into())
          .collect(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        nodes: msg.nodes
          .iter()
          .map(|elem| elem.as_str().into())
          .collect(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      nodes: msg.nodes
          .into_iter()
          .map(|elem| elem.to_string())
          .collect(),
    }
  }
}


// Corresponds to rosapi_msgs__srv__NodeDetails_Request

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct NodeDetails_Request {

    // This member is not documented.
    #[allow(missing_docs)]
    pub node: std::string::String,

}



impl Default for NodeDetails_Request {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::srv::rmw::NodeDetails_Request::default())
  }
}

impl rosidl_runtime_rs::Message for NodeDetails_Request {
  type RmwMsg = super::srv::rmw::NodeDetails_Request;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        node: msg.node.as_str().into(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        node: msg.node.as_str().into(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      node: msg.node.to_string(),
    }
  }
}


// Corresponds to rosapi_msgs__srv__NodeDetails_Response

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct NodeDetails_Response {

    // This member is not documented.
    #[allow(missing_docs)]
    pub subscribing: Vec<std::string::String>,


    // This member is not documented.
    #[allow(missing_docs)]
    pub publishing: Vec<std::string::String>,


    // This member is not documented.
    #[allow(missing_docs)]
    pub services: Vec<std::string::String>,

}



impl Default for NodeDetails_Response {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::srv::rmw::NodeDetails_Response::default())
  }
}

impl rosidl_runtime_rs::Message for NodeDetails_Response {
  type RmwMsg = super::srv::rmw::NodeDetails_Response;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        subscribing: msg.subscribing
          .into_iter()
          .map(|elem| elem.as_str().into())
          .collect(),
        publishing: msg.publishing
          .into_iter()
          .map(|elem| elem.as_str().into())
          .collect(),
        services: msg.services
          .into_iter()
          .map(|elem| elem.as_str().into())
          .collect(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        subscribing: msg.subscribing
          .iter()
          .map(|elem| elem.as_str().into())
          .collect(),
        publishing: msg.publishing
          .iter()
          .map(|elem| elem.as_str().into())
          .collect(),
        services: msg.services
          .iter()
          .map(|elem| elem.as_str().into())
          .collect(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      subscribing: msg.subscribing
          .into_iter()
          .map(|elem| elem.to_string())
          .collect(),
      publishing: msg.publishing
          .into_iter()
          .map(|elem| elem.to_string())
          .collect(),
      services: msg.services
          .into_iter()
          .map(|elem| elem.to_string())
          .collect(),
    }
  }
}


// Corresponds to rosapi_msgs__srv__Publishers_Request

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Publishers_Request {

    // This member is not documented.
    #[allow(missing_docs)]
    pub topic: std::string::String,

}



impl Default for Publishers_Request {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::srv::rmw::Publishers_Request::default())
  }
}

impl rosidl_runtime_rs::Message for Publishers_Request {
  type RmwMsg = super::srv::rmw::Publishers_Request;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        topic: msg.topic.as_str().into(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        topic: msg.topic.as_str().into(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      topic: msg.topic.to_string(),
    }
  }
}


// Corresponds to rosapi_msgs__srv__Publishers_Response

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Publishers_Response {

    // This member is not documented.
    #[allow(missing_docs)]
    pub publishers: Vec<std::string::String>,

}



impl Default for Publishers_Response {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::srv::rmw::Publishers_Response::default())
  }
}

impl rosidl_runtime_rs::Message for Publishers_Response {
  type RmwMsg = super::srv::rmw::Publishers_Response;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        publishers: msg.publishers
          .into_iter()
          .map(|elem| elem.as_str().into())
          .collect(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        publishers: msg.publishers
          .iter()
          .map(|elem| elem.as_str().into())
          .collect(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      publishers: msg.publishers
          .into_iter()
          .map(|elem| elem.to_string())
          .collect(),
    }
  }
}


// Corresponds to rosapi_msgs__srv__ServiceNode_Request

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct ServiceNode_Request {

    // This member is not documented.
    #[allow(missing_docs)]
    pub service: std::string::String,

}



impl Default for ServiceNode_Request {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::srv::rmw::ServiceNode_Request::default())
  }
}

impl rosidl_runtime_rs::Message for ServiceNode_Request {
  type RmwMsg = super::srv::rmw::ServiceNode_Request;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        service: msg.service.as_str().into(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        service: msg.service.as_str().into(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      service: msg.service.to_string(),
    }
  }
}


// Corresponds to rosapi_msgs__srv__ServiceNode_Response

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct ServiceNode_Response {

    // This member is not documented.
    #[allow(missing_docs)]
    pub node: std::string::String,

}



impl Default for ServiceNode_Response {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::srv::rmw::ServiceNode_Response::default())
  }
}

impl rosidl_runtime_rs::Message for ServiceNode_Response {
  type RmwMsg = super::srv::rmw::ServiceNode_Response;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        node: msg.node.as_str().into(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        node: msg.node.as_str().into(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      node: msg.node.to_string(),
    }
  }
}


// Corresponds to rosapi_msgs__srv__ServiceProviders_Request

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct ServiceProviders_Request {

    // This member is not documented.
    #[allow(missing_docs)]
    pub service: std::string::String,

}



impl Default for ServiceProviders_Request {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::srv::rmw::ServiceProviders_Request::default())
  }
}

impl rosidl_runtime_rs::Message for ServiceProviders_Request {
  type RmwMsg = super::srv::rmw::ServiceProviders_Request;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        service: msg.service.as_str().into(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        service: msg.service.as_str().into(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      service: msg.service.to_string(),
    }
  }
}


// Corresponds to rosapi_msgs__srv__ServiceProviders_Response

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct ServiceProviders_Response {

    // This member is not documented.
    #[allow(missing_docs)]
    pub providers: Vec<std::string::String>,

}



impl Default for ServiceProviders_Response {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::srv::rmw::ServiceProviders_Response::default())
  }
}

impl rosidl_runtime_rs::Message for ServiceProviders_Response {
  type RmwMsg = super::srv::rmw::ServiceProviders_Response;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        providers: msg.providers
          .into_iter()
          .map(|elem| elem.as_str().into())
          .collect(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        providers: msg.providers
          .iter()
          .map(|elem| elem.as_str().into())
          .collect(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      providers: msg.providers
          .into_iter()
          .map(|elem| elem.to_string())
          .collect(),
    }
  }
}


// Corresponds to rosapi_msgs__srv__ServiceRequestDetails_Request

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct ServiceRequestDetails_Request {

    // This member is not documented.
    #[allow(missing_docs)]
    pub type_: std::string::String,

}



impl Default for ServiceRequestDetails_Request {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::srv::rmw::ServiceRequestDetails_Request::default())
  }
}

impl rosidl_runtime_rs::Message for ServiceRequestDetails_Request {
  type RmwMsg = super::srv::rmw::ServiceRequestDetails_Request;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        type_: msg.type_.as_str().into(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        type_: msg.type_.as_str().into(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      type_: msg.type_.to_string(),
    }
  }
}


// Corresponds to rosapi_msgs__srv__ServiceRequestDetails_Response

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct ServiceRequestDetails_Response {

    // This member is not documented.
    #[allow(missing_docs)]
    pub typedefs: Vec<super::msg::TypeDef>,

}



impl Default for ServiceRequestDetails_Response {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::srv::rmw::ServiceRequestDetails_Response::default())
  }
}

impl rosidl_runtime_rs::Message for ServiceRequestDetails_Response {
  type RmwMsg = super::srv::rmw::ServiceRequestDetails_Response;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        typedefs: msg.typedefs
          .into_iter()
          .map(|elem| super::msg::TypeDef::into_rmw_message(std::borrow::Cow::Owned(elem)).into_owned())
          .collect(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        typedefs: msg.typedefs
          .iter()
          .map(|elem| super::msg::TypeDef::into_rmw_message(std::borrow::Cow::Borrowed(elem)).into_owned())
          .collect(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      typedefs: msg.typedefs
          .into_iter()
          .map(super::msg::TypeDef::from_rmw_message)
          .collect(),
    }
  }
}


// Corresponds to rosapi_msgs__srv__ServiceResponseDetails_Request

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct ServiceResponseDetails_Request {

    // This member is not documented.
    #[allow(missing_docs)]
    pub type_: std::string::String,

}



impl Default for ServiceResponseDetails_Request {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::srv::rmw::ServiceResponseDetails_Request::default())
  }
}

impl rosidl_runtime_rs::Message for ServiceResponseDetails_Request {
  type RmwMsg = super::srv::rmw::ServiceResponseDetails_Request;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        type_: msg.type_.as_str().into(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        type_: msg.type_.as_str().into(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      type_: msg.type_.to_string(),
    }
  }
}


// Corresponds to rosapi_msgs__srv__ServiceResponseDetails_Response

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct ServiceResponseDetails_Response {

    // This member is not documented.
    #[allow(missing_docs)]
    pub typedefs: Vec<super::msg::TypeDef>,

}



impl Default for ServiceResponseDetails_Response {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::srv::rmw::ServiceResponseDetails_Response::default())
  }
}

impl rosidl_runtime_rs::Message for ServiceResponseDetails_Response {
  type RmwMsg = super::srv::rmw::ServiceResponseDetails_Response;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        typedefs: msg.typedefs
          .into_iter()
          .map(|elem| super::msg::TypeDef::into_rmw_message(std::borrow::Cow::Owned(elem)).into_owned())
          .collect(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        typedefs: msg.typedefs
          .iter()
          .map(|elem| super::msg::TypeDef::into_rmw_message(std::borrow::Cow::Borrowed(elem)).into_owned())
          .collect(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      typedefs: msg.typedefs
          .into_iter()
          .map(super::msg::TypeDef::from_rmw_message)
          .collect(),
    }
  }
}


// Corresponds to rosapi_msgs__srv__Services_Request

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Services_Request {

    // This member is not documented.
    #[allow(missing_docs)]
    pub structure_needs_at_least_one_member: u8,

}



impl Default for Services_Request {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::srv::rmw::Services_Request::default())
  }
}

impl rosidl_runtime_rs::Message for Services_Request {
  type RmwMsg = super::srv::rmw::Services_Request;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        structure_needs_at_least_one_member: msg.structure_needs_at_least_one_member,
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
      structure_needs_at_least_one_member: msg.structure_needs_at_least_one_member,
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      structure_needs_at_least_one_member: msg.structure_needs_at_least_one_member,
    }
  }
}


// Corresponds to rosapi_msgs__srv__Services_Response

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Services_Response {

    // This member is not documented.
    #[allow(missing_docs)]
    pub services: Vec<std::string::String>,

}



impl Default for Services_Response {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::srv::rmw::Services_Response::default())
  }
}

impl rosidl_runtime_rs::Message for Services_Response {
  type RmwMsg = super::srv::rmw::Services_Response;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        services: msg.services
          .into_iter()
          .map(|elem| elem.as_str().into())
          .collect(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        services: msg.services
          .iter()
          .map(|elem| elem.as_str().into())
          .collect(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      services: msg.services
          .into_iter()
          .map(|elem| elem.to_string())
          .collect(),
    }
  }
}


// Corresponds to rosapi_msgs__srv__ServicesForType_Request

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct ServicesForType_Request {

    // This member is not documented.
    #[allow(missing_docs)]
    pub type_: std::string::String,

}



impl Default for ServicesForType_Request {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::srv::rmw::ServicesForType_Request::default())
  }
}

impl rosidl_runtime_rs::Message for ServicesForType_Request {
  type RmwMsg = super::srv::rmw::ServicesForType_Request;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        type_: msg.type_.as_str().into(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        type_: msg.type_.as_str().into(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      type_: msg.type_.to_string(),
    }
  }
}


// Corresponds to rosapi_msgs__srv__ServicesForType_Response

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct ServicesForType_Response {

    // This member is not documented.
    #[allow(missing_docs)]
    pub services: Vec<std::string::String>,

}



impl Default for ServicesForType_Response {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::srv::rmw::ServicesForType_Response::default())
  }
}

impl rosidl_runtime_rs::Message for ServicesForType_Response {
  type RmwMsg = super::srv::rmw::ServicesForType_Response;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        services: msg.services
          .into_iter()
          .map(|elem| elem.as_str().into())
          .collect(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        services: msg.services
          .iter()
          .map(|elem| elem.as_str().into())
          .collect(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      services: msg.services
          .into_iter()
          .map(|elem| elem.to_string())
          .collect(),
    }
  }
}


// Corresponds to rosapi_msgs__srv__ServiceType_Request

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct ServiceType_Request {

    // This member is not documented.
    #[allow(missing_docs)]
    pub service: std::string::String,

}



impl Default for ServiceType_Request {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::srv::rmw::ServiceType_Request::default())
  }
}

impl rosidl_runtime_rs::Message for ServiceType_Request {
  type RmwMsg = super::srv::rmw::ServiceType_Request;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        service: msg.service.as_str().into(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        service: msg.service.as_str().into(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      service: msg.service.to_string(),
    }
  }
}


// Corresponds to rosapi_msgs__srv__ServiceType_Response

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct ServiceType_Response {

    // This member is not documented.
    #[allow(missing_docs)]
    pub type_: std::string::String,

}



impl Default for ServiceType_Response {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::srv::rmw::ServiceType_Response::default())
  }
}

impl rosidl_runtime_rs::Message for ServiceType_Response {
  type RmwMsg = super::srv::rmw::ServiceType_Response;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        type_: msg.type_.as_str().into(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        type_: msg.type_.as_str().into(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      type_: msg.type_.to_string(),
    }
  }
}


// Corresponds to rosapi_msgs__srv__SetParam_Request

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct SetParam_Request {

    // This member is not documented.
    #[allow(missing_docs)]
    pub name: std::string::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub value: std::string::String,

}



impl Default for SetParam_Request {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::srv::rmw::SetParam_Request::default())
  }
}

impl rosidl_runtime_rs::Message for SetParam_Request {
  type RmwMsg = super::srv::rmw::SetParam_Request;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        name: msg.name.as_str().into(),
        value: msg.value.as_str().into(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        name: msg.name.as_str().into(),
        value: msg.value.as_str().into(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      name: msg.name.to_string(),
      value: msg.value.to_string(),
    }
  }
}


// Corresponds to rosapi_msgs__srv__SetParam_Response

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct SetParam_Response {

    // This member is not documented.
    #[allow(missing_docs)]
    pub structure_needs_at_least_one_member: u8,

}



impl Default for SetParam_Response {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::srv::rmw::SetParam_Response::default())
  }
}

impl rosidl_runtime_rs::Message for SetParam_Response {
  type RmwMsg = super::srv::rmw::SetParam_Response;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        structure_needs_at_least_one_member: msg.structure_needs_at_least_one_member,
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
      structure_needs_at_least_one_member: msg.structure_needs_at_least_one_member,
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      structure_needs_at_least_one_member: msg.structure_needs_at_least_one_member,
    }
  }
}


// Corresponds to rosapi_msgs__srv__Subscribers_Request

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Subscribers_Request {

    // This member is not documented.
    #[allow(missing_docs)]
    pub topic: std::string::String,

}



impl Default for Subscribers_Request {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::srv::rmw::Subscribers_Request::default())
  }
}

impl rosidl_runtime_rs::Message for Subscribers_Request {
  type RmwMsg = super::srv::rmw::Subscribers_Request;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        topic: msg.topic.as_str().into(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        topic: msg.topic.as_str().into(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      topic: msg.topic.to_string(),
    }
  }
}


// Corresponds to rosapi_msgs__srv__Subscribers_Response

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Subscribers_Response {

    // This member is not documented.
    #[allow(missing_docs)]
    pub subscribers: Vec<std::string::String>,

}



impl Default for Subscribers_Response {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::srv::rmw::Subscribers_Response::default())
  }
}

impl rosidl_runtime_rs::Message for Subscribers_Response {
  type RmwMsg = super::srv::rmw::Subscribers_Response;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        subscribers: msg.subscribers
          .into_iter()
          .map(|elem| elem.as_str().into())
          .collect(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        subscribers: msg.subscribers
          .iter()
          .map(|elem| elem.as_str().into())
          .collect(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      subscribers: msg.subscribers
          .into_iter()
          .map(|elem| elem.to_string())
          .collect(),
    }
  }
}


// Corresponds to rosapi_msgs__srv__Topics_Request

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Topics_Request {

    // This member is not documented.
    #[allow(missing_docs)]
    pub structure_needs_at_least_one_member: u8,

}



impl Default for Topics_Request {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::srv::rmw::Topics_Request::default())
  }
}

impl rosidl_runtime_rs::Message for Topics_Request {
  type RmwMsg = super::srv::rmw::Topics_Request;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        structure_needs_at_least_one_member: msg.structure_needs_at_least_one_member,
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
      structure_needs_at_least_one_member: msg.structure_needs_at_least_one_member,
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      structure_needs_at_least_one_member: msg.structure_needs_at_least_one_member,
    }
  }
}


// Corresponds to rosapi_msgs__srv__Topics_Response

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Topics_Response {

    // This member is not documented.
    #[allow(missing_docs)]
    pub topics: Vec<std::string::String>,


    // This member is not documented.
    #[allow(missing_docs)]
    pub types: Vec<std::string::String>,

}



impl Default for Topics_Response {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::srv::rmw::Topics_Response::default())
  }
}

impl rosidl_runtime_rs::Message for Topics_Response {
  type RmwMsg = super::srv::rmw::Topics_Response;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        topics: msg.topics
          .into_iter()
          .map(|elem| elem.as_str().into())
          .collect(),
        types: msg.types
          .into_iter()
          .map(|elem| elem.as_str().into())
          .collect(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        topics: msg.topics
          .iter()
          .map(|elem| elem.as_str().into())
          .collect(),
        types: msg.types
          .iter()
          .map(|elem| elem.as_str().into())
          .collect(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      topics: msg.topics
          .into_iter()
          .map(|elem| elem.to_string())
          .collect(),
      types: msg.types
          .into_iter()
          .map(|elem| elem.to_string())
          .collect(),
    }
  }
}


// Corresponds to rosapi_msgs__srv__TopicsAndRawTypes_Request

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct TopicsAndRawTypes_Request {

    // This member is not documented.
    #[allow(missing_docs)]
    pub structure_needs_at_least_one_member: u8,

}



impl Default for TopicsAndRawTypes_Request {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::srv::rmw::TopicsAndRawTypes_Request::default())
  }
}

impl rosidl_runtime_rs::Message for TopicsAndRawTypes_Request {
  type RmwMsg = super::srv::rmw::TopicsAndRawTypes_Request;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        structure_needs_at_least_one_member: msg.structure_needs_at_least_one_member,
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
      structure_needs_at_least_one_member: msg.structure_needs_at_least_one_member,
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      structure_needs_at_least_one_member: msg.structure_needs_at_least_one_member,
    }
  }
}


// Corresponds to rosapi_msgs__srv__TopicsAndRawTypes_Response

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct TopicsAndRawTypes_Response {

    // This member is not documented.
    #[allow(missing_docs)]
    pub topics: Vec<std::string::String>,


    // This member is not documented.
    #[allow(missing_docs)]
    pub types: Vec<std::string::String>,


    // This member is not documented.
    #[allow(missing_docs)]
    pub typedefs_full_text: Vec<std::string::String>,

}



impl Default for TopicsAndRawTypes_Response {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::srv::rmw::TopicsAndRawTypes_Response::default())
  }
}

impl rosidl_runtime_rs::Message for TopicsAndRawTypes_Response {
  type RmwMsg = super::srv::rmw::TopicsAndRawTypes_Response;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        topics: msg.topics
          .into_iter()
          .map(|elem| elem.as_str().into())
          .collect(),
        types: msg.types
          .into_iter()
          .map(|elem| elem.as_str().into())
          .collect(),
        typedefs_full_text: msg.typedefs_full_text
          .into_iter()
          .map(|elem| elem.as_str().into())
          .collect(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        topics: msg.topics
          .iter()
          .map(|elem| elem.as_str().into())
          .collect(),
        types: msg.types
          .iter()
          .map(|elem| elem.as_str().into())
          .collect(),
        typedefs_full_text: msg.typedefs_full_text
          .iter()
          .map(|elem| elem.as_str().into())
          .collect(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      topics: msg.topics
          .into_iter()
          .map(|elem| elem.to_string())
          .collect(),
      types: msg.types
          .into_iter()
          .map(|elem| elem.to_string())
          .collect(),
      typedefs_full_text: msg.typedefs_full_text
          .into_iter()
          .map(|elem| elem.to_string())
          .collect(),
    }
  }
}


// Corresponds to rosapi_msgs__srv__TopicsForType_Request

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct TopicsForType_Request {

    // This member is not documented.
    #[allow(missing_docs)]
    pub type_: std::string::String,

}



impl Default for TopicsForType_Request {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::srv::rmw::TopicsForType_Request::default())
  }
}

impl rosidl_runtime_rs::Message for TopicsForType_Request {
  type RmwMsg = super::srv::rmw::TopicsForType_Request;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        type_: msg.type_.as_str().into(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        type_: msg.type_.as_str().into(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      type_: msg.type_.to_string(),
    }
  }
}


// Corresponds to rosapi_msgs__srv__TopicsForType_Response

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct TopicsForType_Response {

    // This member is not documented.
    #[allow(missing_docs)]
    pub topics: Vec<std::string::String>,

}



impl Default for TopicsForType_Response {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::srv::rmw::TopicsForType_Response::default())
  }
}

impl rosidl_runtime_rs::Message for TopicsForType_Response {
  type RmwMsg = super::srv::rmw::TopicsForType_Response;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        topics: msg.topics
          .into_iter()
          .map(|elem| elem.as_str().into())
          .collect(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        topics: msg.topics
          .iter()
          .map(|elem| elem.as_str().into())
          .collect(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      topics: msg.topics
          .into_iter()
          .map(|elem| elem.to_string())
          .collect(),
    }
  }
}


// Corresponds to rosapi_msgs__srv__TopicType_Request

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct TopicType_Request {

    // This member is not documented.
    #[allow(missing_docs)]
    pub topic: std::string::String,

}



impl Default for TopicType_Request {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::srv::rmw::TopicType_Request::default())
  }
}

impl rosidl_runtime_rs::Message for TopicType_Request {
  type RmwMsg = super::srv::rmw::TopicType_Request;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        topic: msg.topic.as_str().into(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        topic: msg.topic.as_str().into(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      topic: msg.topic.to_string(),
    }
  }
}


// Corresponds to rosapi_msgs__srv__TopicType_Response

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct TopicType_Response {

    // This member is not documented.
    #[allow(missing_docs)]
    pub type_: std::string::String,

}



impl Default for TopicType_Response {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::srv::rmw::TopicType_Response::default())
  }
}

impl rosidl_runtime_rs::Message for TopicType_Response {
  type RmwMsg = super::srv::rmw::TopicType_Response;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        type_: msg.type_.as_str().into(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        type_: msg.type_.as_str().into(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      type_: msg.type_.to_string(),
    }
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


