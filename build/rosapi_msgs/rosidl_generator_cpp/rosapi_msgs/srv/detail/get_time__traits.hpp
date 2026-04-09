// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from rosapi_msgs:srv/GetTime.idl
// generated code does not contain a copyright notice

#ifndef ROSAPI_MSGS__SRV__DETAIL__GET_TIME__TRAITS_HPP_
#define ROSAPI_MSGS__SRV__DETAIL__GET_TIME__TRAITS_HPP_

#include "rosapi_msgs/srv/detail/get_time__struct.hpp"
#include <rosidl_runtime_cpp/traits.hpp>
#include <stdint.h>
#include <type_traits>

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<rosapi_msgs::srv::GetTime_Request>()
{
  return "rosapi_msgs::srv::GetTime_Request";
}

template<>
inline const char * name<rosapi_msgs::srv::GetTime_Request>()
{
  return "rosapi_msgs/srv/GetTime_Request";
}

template<>
struct has_fixed_size<rosapi_msgs::srv::GetTime_Request>
  : std::integral_constant<bool, true> {};

template<>
struct has_bounded_size<rosapi_msgs::srv::GetTime_Request>
  : std::integral_constant<bool, true> {};

template<>
struct is_message<rosapi_msgs::srv::GetTime_Request>
  : std::true_type {};

}  // namespace rosidl_generator_traits

// Include directives for member types
// Member 'time'
#include "builtin_interfaces/msg/detail/time__traits.hpp"

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<rosapi_msgs::srv::GetTime_Response>()
{
  return "rosapi_msgs::srv::GetTime_Response";
}

template<>
inline const char * name<rosapi_msgs::srv::GetTime_Response>()
{
  return "rosapi_msgs/srv/GetTime_Response";
}

template<>
struct has_fixed_size<rosapi_msgs::srv::GetTime_Response>
  : std::integral_constant<bool, has_fixed_size<builtin_interfaces::msg::Time>::value> {};

template<>
struct has_bounded_size<rosapi_msgs::srv::GetTime_Response>
  : std::integral_constant<bool, has_bounded_size<builtin_interfaces::msg::Time>::value> {};

template<>
struct is_message<rosapi_msgs::srv::GetTime_Response>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<rosapi_msgs::srv::GetTime>()
{
  return "rosapi_msgs::srv::GetTime";
}

template<>
inline const char * name<rosapi_msgs::srv::GetTime>()
{
  return "rosapi_msgs/srv/GetTime";
}

template<>
struct has_fixed_size<rosapi_msgs::srv::GetTime>
  : std::integral_constant<
    bool,
    has_fixed_size<rosapi_msgs::srv::GetTime_Request>::value &&
    has_fixed_size<rosapi_msgs::srv::GetTime_Response>::value
  >
{
};

template<>
struct has_bounded_size<rosapi_msgs::srv::GetTime>
  : std::integral_constant<
    bool,
    has_bounded_size<rosapi_msgs::srv::GetTime_Request>::value &&
    has_bounded_size<rosapi_msgs::srv::GetTime_Response>::value
  >
{
};

template<>
struct is_service<rosapi_msgs::srv::GetTime>
  : std::true_type
{
};

template<>
struct is_service_request<rosapi_msgs::srv::GetTime_Request>
  : std::true_type
{
};

template<>
struct is_service_response<rosapi_msgs::srv::GetTime_Response>
  : std::true_type
{
};

}  // namespace rosidl_generator_traits

#endif  // ROSAPI_MSGS__SRV__DETAIL__GET_TIME__TRAITS_HPP_
