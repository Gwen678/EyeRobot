// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from rosapi_msgs:srv/NodeDetails.idl
// generated code does not contain a copyright notice

#ifndef ROSAPI_MSGS__SRV__DETAIL__NODE_DETAILS__TRAITS_HPP_
#define ROSAPI_MSGS__SRV__DETAIL__NODE_DETAILS__TRAITS_HPP_

#include "rosapi_msgs/srv/detail/node_details__struct.hpp"
#include <rosidl_runtime_cpp/traits.hpp>
#include <stdint.h>
#include <type_traits>

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<rosapi_msgs::srv::NodeDetails_Request>()
{
  return "rosapi_msgs::srv::NodeDetails_Request";
}

template<>
inline const char * name<rosapi_msgs::srv::NodeDetails_Request>()
{
  return "rosapi_msgs/srv/NodeDetails_Request";
}

template<>
struct has_fixed_size<rosapi_msgs::srv::NodeDetails_Request>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<rosapi_msgs::srv::NodeDetails_Request>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<rosapi_msgs::srv::NodeDetails_Request>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<rosapi_msgs::srv::NodeDetails_Response>()
{
  return "rosapi_msgs::srv::NodeDetails_Response";
}

template<>
inline const char * name<rosapi_msgs::srv::NodeDetails_Response>()
{
  return "rosapi_msgs/srv/NodeDetails_Response";
}

template<>
struct has_fixed_size<rosapi_msgs::srv::NodeDetails_Response>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<rosapi_msgs::srv::NodeDetails_Response>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<rosapi_msgs::srv::NodeDetails_Response>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<rosapi_msgs::srv::NodeDetails>()
{
  return "rosapi_msgs::srv::NodeDetails";
}

template<>
inline const char * name<rosapi_msgs::srv::NodeDetails>()
{
  return "rosapi_msgs/srv/NodeDetails";
}

template<>
struct has_fixed_size<rosapi_msgs::srv::NodeDetails>
  : std::integral_constant<
    bool,
    has_fixed_size<rosapi_msgs::srv::NodeDetails_Request>::value &&
    has_fixed_size<rosapi_msgs::srv::NodeDetails_Response>::value
  >
{
};

template<>
struct has_bounded_size<rosapi_msgs::srv::NodeDetails>
  : std::integral_constant<
    bool,
    has_bounded_size<rosapi_msgs::srv::NodeDetails_Request>::value &&
    has_bounded_size<rosapi_msgs::srv::NodeDetails_Response>::value
  >
{
};

template<>
struct is_service<rosapi_msgs::srv::NodeDetails>
  : std::true_type
{
};

template<>
struct is_service_request<rosapi_msgs::srv::NodeDetails_Request>
  : std::true_type
{
};

template<>
struct is_service_response<rosapi_msgs::srv::NodeDetails_Response>
  : std::true_type
{
};

}  // namespace rosidl_generator_traits

#endif  // ROSAPI_MSGS__SRV__DETAIL__NODE_DETAILS__TRAITS_HPP_
