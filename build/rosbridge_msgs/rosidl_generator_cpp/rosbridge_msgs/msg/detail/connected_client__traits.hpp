// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from rosbridge_msgs:msg/ConnectedClient.idl
// generated code does not contain a copyright notice

#ifndef ROSBRIDGE_MSGS__MSG__DETAIL__CONNECTED_CLIENT__TRAITS_HPP_
#define ROSBRIDGE_MSGS__MSG__DETAIL__CONNECTED_CLIENT__TRAITS_HPP_

#include "rosbridge_msgs/msg/detail/connected_client__struct.hpp"
#include <rosidl_runtime_cpp/traits.hpp>
#include <stdint.h>
#include <type_traits>

// Include directives for member types
// Member 'connection_time'
#include "builtin_interfaces/msg/detail/time__traits.hpp"

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<rosbridge_msgs::msg::ConnectedClient>()
{
  return "rosbridge_msgs::msg::ConnectedClient";
}

template<>
inline const char * name<rosbridge_msgs::msg::ConnectedClient>()
{
  return "rosbridge_msgs/msg/ConnectedClient";
}

template<>
struct has_fixed_size<rosbridge_msgs::msg::ConnectedClient>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<rosbridge_msgs::msg::ConnectedClient>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<rosbridge_msgs::msg::ConnectedClient>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // ROSBRIDGE_MSGS__MSG__DETAIL__CONNECTED_CLIENT__TRAITS_HPP_
