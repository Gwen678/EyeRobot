// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from rosapi_msgs:srv/GetParam.idl
// generated code does not contain a copyright notice

#ifndef ROSAPI_MSGS__SRV__DETAIL__GET_PARAM__TRAITS_HPP_
#define ROSAPI_MSGS__SRV__DETAIL__GET_PARAM__TRAITS_HPP_

#include "rosapi_msgs/srv/detail/get_param__struct.hpp"
#include <rosidl_runtime_cpp/traits.hpp>
#include <stdint.h>
#include <type_traits>

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<rosapi_msgs::srv::GetParam_Request>()
{
  return "rosapi_msgs::srv::GetParam_Request";
}

template<>
inline const char * name<rosapi_msgs::srv::GetParam_Request>()
{
  return "rosapi_msgs/srv/GetParam_Request";
}

template<>
struct has_fixed_size<rosapi_msgs::srv::GetParam_Request>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<rosapi_msgs::srv::GetParam_Request>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<rosapi_msgs::srv::GetParam_Request>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<rosapi_msgs::srv::GetParam_Response>()
{
  return "rosapi_msgs::srv::GetParam_Response";
}

template<>
inline const char * name<rosapi_msgs::srv::GetParam_Response>()
{
  return "rosapi_msgs/srv/GetParam_Response";
}

template<>
struct has_fixed_size<rosapi_msgs::srv::GetParam_Response>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<rosapi_msgs::srv::GetParam_Response>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<rosapi_msgs::srv::GetParam_Response>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<rosapi_msgs::srv::GetParam>()
{
  return "rosapi_msgs::srv::GetParam";
}

template<>
inline const char * name<rosapi_msgs::srv::GetParam>()
{
  return "rosapi_msgs/srv/GetParam";
}

template<>
struct has_fixed_size<rosapi_msgs::srv::GetParam>
  : std::integral_constant<
    bool,
    has_fixed_size<rosapi_msgs::srv::GetParam_Request>::value &&
    has_fixed_size<rosapi_msgs::srv::GetParam_Response>::value
  >
{
};

template<>
struct has_bounded_size<rosapi_msgs::srv::GetParam>
  : std::integral_constant<
    bool,
    has_bounded_size<rosapi_msgs::srv::GetParam_Request>::value &&
    has_bounded_size<rosapi_msgs::srv::GetParam_Response>::value
  >
{
};

template<>
struct is_service<rosapi_msgs::srv::GetParam>
  : std::true_type
{
};

template<>
struct is_service_request<rosapi_msgs::srv::GetParam_Request>
  : std::true_type
{
};

template<>
struct is_service_response<rosapi_msgs::srv::GetParam_Response>
  : std::true_type
{
};

}  // namespace rosidl_generator_traits

#endif  // ROSAPI_MSGS__SRV__DETAIL__GET_PARAM__TRAITS_HPP_
