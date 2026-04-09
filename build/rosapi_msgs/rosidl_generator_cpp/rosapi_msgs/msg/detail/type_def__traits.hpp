// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from rosapi_msgs:msg/TypeDef.idl
// generated code does not contain a copyright notice

#ifndef ROSAPI_MSGS__MSG__DETAIL__TYPE_DEF__TRAITS_HPP_
#define ROSAPI_MSGS__MSG__DETAIL__TYPE_DEF__TRAITS_HPP_

#include "rosapi_msgs/msg/detail/type_def__struct.hpp"
#include <rosidl_runtime_cpp/traits.hpp>
#include <stdint.h>
#include <type_traits>

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<rosapi_msgs::msg::TypeDef>()
{
  return "rosapi_msgs::msg::TypeDef";
}

template<>
inline const char * name<rosapi_msgs::msg::TypeDef>()
{
  return "rosapi_msgs/msg/TypeDef";
}

template<>
struct has_fixed_size<rosapi_msgs::msg::TypeDef>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<rosapi_msgs::msg::TypeDef>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<rosapi_msgs::msg::TypeDef>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // ROSAPI_MSGS__MSG__DETAIL__TYPE_DEF__TRAITS_HPP_
