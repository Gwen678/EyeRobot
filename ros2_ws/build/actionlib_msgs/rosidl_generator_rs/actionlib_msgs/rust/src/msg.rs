#[cfg(feature = "serde")]
use serde::{Deserialize, Serialize};



// Corresponds to actionlib_msgs__msg__GoalID

// This struct is not documented.
#[allow(missing_docs)]

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct GoalID {
    /// The stamp should store the time at which this goal was requested.
    /// It is used by an action server when it tries to preempt all
    /// goals that were requested before a certain time
    pub stamp: builtin_interfaces::msg::Time,

    /// The id provides a way to associate feedback and
    /// result message with specific goal requests. The id
    /// specified must be unique.
    pub id: std::string::String,

}



impl Default for GoalID {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::GoalID::default())
  }
}

impl rosidl_runtime_rs::Message for GoalID {
  type RmwMsg = super::msg::rmw::GoalID;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        stamp: builtin_interfaces::msg::Time::into_rmw_message(std::borrow::Cow::Owned(msg.stamp)).into_owned(),
        id: msg.id.as_str().into(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        stamp: builtin_interfaces::msg::Time::into_rmw_message(std::borrow::Cow::Borrowed(&msg.stamp)).into_owned(),
        id: msg.id.as_str().into(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      stamp: builtin_interfaces::msg::Time::from_rmw_message(msg.stamp),
      id: msg.id.to_string(),
    }
  }
}


// Corresponds to actionlib_msgs__msg__GoalStatus

// This struct is not documented.
#[allow(missing_docs)]

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct GoalStatus {

    // This member is not documented.
    #[allow(missing_docs)]
    pub goal_id: super::msg::GoalID,


    // This member is not documented.
    #[allow(missing_docs)]
    pub status: u8,

    /// Allow for the user to associate a string with GoalStatus for debugging.
    pub text: std::string::String,

}

impl GoalStatus {
    /// The goal has yet to be processed by the action server.
    pub const PENDING: u8 = 0;

    /// The goal is currently being processed by the action server.
    pub const ACTIVE: u8 = 1;

    /// The goal received a cancel request after it started executing
    ///   and has since completed its execution (Terminal State).
    pub const PREEMPTED: u8 = 2;

    /// The goal was achieved successfully by the action server
    ///   (Terminal State).
    pub const SUCCEEDED: u8 = 3;

    /// The goal was aborted during execution by the action server due
    ///    to some failure (Terminal State).
    pub const ABORTED: u8 = 4;

    /// The goal was rejected by the action server without being processed,
    ///    because the goal was unattainable or invalid (Terminal State).
    pub const REJECTED: u8 = 5;

    /// The goal received a cancel request after it started executing
    ///    and has not yet completed execution.
    pub const PREEMPTING: u8 = 6;

    /// The goal received a cancel request before it started executing, but
    ///    the action server has not yet confirmed that the goal is canceled.
    pub const RECALLING: u8 = 7;

    /// The goal received a cancel request before it started executing
    ///    and was successfully cancelled (Terminal State).
    pub const RECALLED: u8 = 8;

    /// An action client can determine that a goal is LOST. This should not
    ///    be sent over the wire by an action server.
    pub const LOST: u8 = 9;

}


impl Default for GoalStatus {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::GoalStatus::default())
  }
}

impl rosidl_runtime_rs::Message for GoalStatus {
  type RmwMsg = super::msg::rmw::GoalStatus;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        goal_id: super::msg::GoalID::into_rmw_message(std::borrow::Cow::Owned(msg.goal_id)).into_owned(),
        status: msg.status,
        text: msg.text.as_str().into(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        goal_id: super::msg::GoalID::into_rmw_message(std::borrow::Cow::Borrowed(&msg.goal_id)).into_owned(),
      status: msg.status,
        text: msg.text.as_str().into(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      goal_id: super::msg::GoalID::from_rmw_message(msg.goal_id),
      status: msg.status,
      text: msg.text.to_string(),
    }
  }
}


// Corresponds to actionlib_msgs__msg__GoalStatusArray
/// Stores the statuses for goals that are currently being tracked
/// by an action server

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct GoalStatusArray {

    // This member is not documented.
    #[allow(missing_docs)]
    pub header: std_msgs::msg::Header,


    // This member is not documented.
    #[allow(missing_docs)]
    pub status_list: Vec<super::msg::GoalStatus>,

}



impl Default for GoalStatusArray {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::GoalStatusArray::default())
  }
}

impl rosidl_runtime_rs::Message for GoalStatusArray {
  type RmwMsg = super::msg::rmw::GoalStatusArray;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        header: std_msgs::msg::Header::into_rmw_message(std::borrow::Cow::Owned(msg.header)).into_owned(),
        status_list: msg.status_list
          .into_iter()
          .map(|elem| super::msg::GoalStatus::into_rmw_message(std::borrow::Cow::Owned(elem)).into_owned())
          .collect(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        header: std_msgs::msg::Header::into_rmw_message(std::borrow::Cow::Borrowed(&msg.header)).into_owned(),
        status_list: msg.status_list
          .iter()
          .map(|elem| super::msg::GoalStatus::into_rmw_message(std::borrow::Cow::Borrowed(elem)).into_owned())
          .collect(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      header: std_msgs::msg::Header::from_rmw_message(msg.header),
      status_list: msg.status_list
          .into_iter()
          .map(super::msg::GoalStatus::from_rmw_message)
          .collect(),
    }
  }
}


