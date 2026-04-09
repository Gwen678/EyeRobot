// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from rosapi_msgs:srv/GetROSVersion.idl
// generated code does not contain a copyright notice

#ifndef ROSAPI_MSGS__SRV__DETAIL__GET_ROS_VERSION__TRAITS_HPP_
#define ROSAPI_MSGS__SRV__DETAIL__GET_ROS_VERSION__TRAITS_HPP_

#include "rosapi_msgs/srv/detail/get_ros_version__struct.hpp"
#include <rosidl_runtime_cpp/traits.hpp>
#include <stdint.h>
#include <type_traits>

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<rosapi_msgs::srv::GetROSVersion_Request>()
{
  return "rosapi_msgs::srv::GetROSVersion_Request";
}

template<>
inline const char * name<rosapi_msgs::srv::GetROSVersion_Request>()
{
  return "rosapi_msgs/srv/GetROSVersion_Request";
}

template<>
struct has_fixed_size<rosapi_msgs::srv::GetROSVersion_Request>
  : std::integral_constant<bool, true> {};

template<>
struct has_bounded_size<rosapi_msgs::srv::GetROSVersion_Request>
  : std::integral_constant<bool, true> {};

template<>
struct is_message<rosapi_msgs::srv::GetROSVersion_Request>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<rosapi_msgs::srv::GetROSVersion_Response>()
{
  return "rosapi_msgs::srv::GetROSVersion_Response";
}

template<>
inline const char * name<rosapi_msgs::srv::GetROSVersion_Response>()
{
  return "rosapi_msgs/srv/GetROSVersion_Response";
}

template<>
struct has_fixed_size<rosapi_msgs::srv::GetROSVersion_Response>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<rosapi_msgs::srv::GetROSVersion_Response>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<rosapi_msgs::srv::GetROSVersion_Response>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<rosapi_msgs::srv::GetROSVersion>()
{
  return "rosapi_msgs::srv::GetROSVersion";
}

template<>
inline const char * name<rosapi_msgs::srv::GetROSVersion>()
{
  return "rosapi_msgs/srv/GetROSVersion";
}

template<>
struct has_fixed_size<rosapi_msgs::srv::GetROSVersion>
  : std::integral_constant<
    bool,
    has_fixed_size<rosapi_msgs::srv::GetROSVersion_Request>::value &&
    has_fixed_size<rosapi_msgs::srv::GetROSVersion_Response>::value
  >
{
};

template<>
struct has_bounded_size<rosapi_msgs::srv::GetROSVersion>
  : std::integral_constant<
    bool,
    has_bounded_size<rosapi_msgs::srv::GetROSVersion_Request>::value &&
    has_bounded_size<rosapi_msgs::srv::GetROSVersion_Response>::value
  >
{
};

template<>
struct is_service<rosapi_msgs::srv::GetROSVersion>
  : std::true_type
{
};

template<>
struct is_service_request<rosapi_msgs::srv::GetROSVersion_Request>
  : std::true_type
{
};

template<>
struct is_service_response<rosapi_msgs::srv::GetROSVersion_Response>
  : std::true_type
{
};

}  // namespace rosidl_generator_traits

#endif  // ROSAPI_MSGS__SRV__DETAIL__GET_ROS_VERSION__TRAITS_HPP_
