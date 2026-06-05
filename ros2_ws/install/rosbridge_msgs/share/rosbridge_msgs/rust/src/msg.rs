#[cfg(feature = "serde")]
use serde::{Deserialize, Serialize};



// Corresponds to rosbridge_msgs__msg__ConnectedClient

// This struct is not documented.
#[allow(missing_docs)]

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct ConnectedClient {

    // This member is not documented.
    #[allow(missing_docs)]
    pub ip_address: std::string::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub connection_time: builtin_interfaces::msg::Time,

}



impl Default for ConnectedClient {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::ConnectedClient::default())
  }
}

impl rosidl_runtime_rs::Message for ConnectedClient {
  type RmwMsg = super::msg::rmw::ConnectedClient;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        ip_address: msg.ip_address.as_str().into(),
        connection_time: builtin_interfaces::msg::Time::into_rmw_message(std::borrow::Cow::Owned(msg.connection_time)).into_owned(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        ip_address: msg.ip_address.as_str().into(),
        connection_time: builtin_interfaces::msg::Time::into_rmw_message(std::borrow::Cow::Borrowed(&msg.connection_time)).into_owned(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      ip_address: msg.ip_address.to_string(),
      connection_time: builtin_interfaces::msg::Time::from_rmw_message(msg.connection_time),
    }
  }
}


// Corresponds to rosbridge_msgs__msg__ConnectedClients

// This struct is not documented.
#[allow(missing_docs)]

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct ConnectedClients {

    // This member is not documented.
    #[allow(missing_docs)]
    pub clients: Vec<super::msg::ConnectedClient>,

}



impl Default for ConnectedClients {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::ConnectedClients::default())
  }
}

impl rosidl_runtime_rs::Message for ConnectedClients {
  type RmwMsg = super::msg::rmw::ConnectedClients;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        clients: msg.clients
          .into_iter()
          .map(|elem| super::msg::ConnectedClient::into_rmw_message(std::borrow::Cow::Owned(elem)).into_owned())
          .collect(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        clients: msg.clients
          .iter()
          .map(|elem| super::msg::ConnectedClient::into_rmw_message(std::borrow::Cow::Borrowed(elem)).into_owned())
          .collect(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      clients: msg.clients
          .into_iter()
          .map(super::msg::ConnectedClient::from_rmw_message)
          .collect(),
    }
  }
}


