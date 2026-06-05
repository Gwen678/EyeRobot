#[cfg(feature = "serde")]
use serde::{Deserialize, Serialize};



// Corresponds to rosapi_msgs__msg__TypeDef

// This struct is not documented.
#[allow(missing_docs)]

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct TypeDef {

    // This member is not documented.
    #[allow(missing_docs)]
    pub type_: std::string::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub fieldnames: Vec<std::string::String>,


    // This member is not documented.
    #[allow(missing_docs)]
    pub fieldtypes: Vec<std::string::String>,


    // This member is not documented.
    #[allow(missing_docs)]
    pub fieldarraylen: Vec<i32>,


    // This member is not documented.
    #[allow(missing_docs)]
    pub examples: Vec<std::string::String>,


    // This member is not documented.
    #[allow(missing_docs)]
    pub constnames: Vec<std::string::String>,


    // This member is not documented.
    #[allow(missing_docs)]
    pub constvalues: Vec<std::string::String>,

}



impl Default for TypeDef {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::TypeDef::default())
  }
}

impl rosidl_runtime_rs::Message for TypeDef {
  type RmwMsg = super::msg::rmw::TypeDef;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        type_: msg.type_.as_str().into(),
        fieldnames: msg.fieldnames
          .into_iter()
          .map(|elem| elem.as_str().into())
          .collect(),
        fieldtypes: msg.fieldtypes
          .into_iter()
          .map(|elem| elem.as_str().into())
          .collect(),
        fieldarraylen: msg.fieldarraylen.into(),
        examples: msg.examples
          .into_iter()
          .map(|elem| elem.as_str().into())
          .collect(),
        constnames: msg.constnames
          .into_iter()
          .map(|elem| elem.as_str().into())
          .collect(),
        constvalues: msg.constvalues
          .into_iter()
          .map(|elem| elem.as_str().into())
          .collect(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        type_: msg.type_.as_str().into(),
        fieldnames: msg.fieldnames
          .iter()
          .map(|elem| elem.as_str().into())
          .collect(),
        fieldtypes: msg.fieldtypes
          .iter()
          .map(|elem| elem.as_str().into())
          .collect(),
        fieldarraylen: msg.fieldarraylen.as_slice().into(),
        examples: msg.examples
          .iter()
          .map(|elem| elem.as_str().into())
          .collect(),
        constnames: msg.constnames
          .iter()
          .map(|elem| elem.as_str().into())
          .collect(),
        constvalues: msg.constvalues
          .iter()
          .map(|elem| elem.as_str().into())
          .collect(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      type_: msg.type_.to_string(),
      fieldnames: msg.fieldnames
          .into_iter()
          .map(|elem| elem.to_string())
          .collect(),
      fieldtypes: msg.fieldtypes
          .into_iter()
          .map(|elem| elem.to_string())
          .collect(),
      fieldarraylen: msg.fieldarraylen
          .into_iter()
          .collect(),
      examples: msg.examples
          .into_iter()
          .map(|elem| elem.to_string())
          .collect(),
      constnames: msg.constnames
          .into_iter()
          .map(|elem| elem.to_string())
          .collect(),
      constvalues: msg.constvalues
          .into_iter()
          .map(|elem| elem.to_string())
          .collect(),
    }
  }
}


