// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from rosbridge_msgs:msg/ConnectedClients.idl
// generated code does not contain a copyright notice

#ifndef ROSBRIDGE_MSGS__MSG__DETAIL__CONNECTED_CLIENTS__TRAITS_HPP_
#define ROSBRIDGE_MSGS__MSG__DETAIL__CONNECTED_CLIENTS__TRAITS_HPP_

#include "rosbridge_msgs/msg/detail/connected_clients__struct.hpp"
#include <rosidl_runtime_cpp/traits.hpp>
#include <stdint.h>
#include <type_traits>

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<rosbridge_msgs::msg::ConnectedClients>()
{
  return "rosbridge_msgs::msg::ConnectedClients";
}

template<>
inline const char * name<rosbridge_msgs::msg::ConnectedClients>()
{
  return "rosbridge_msgs/msg/ConnectedClients";
}

template<>
struct has_fixed_size<rosbridge_msgs::msg::ConnectedClients>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<rosbridge_msgs::msg::ConnectedClients>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<rosbridge_msgs::msg::ConnectedClients>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // ROSBRIDGE_MSGS__MSG__DETAIL__CONNECTED_CLIENTS__TRAITS_HPP_
