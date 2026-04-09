// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from rosbridge_test_msgs:msg/TestHeader.idl
// generated code does not contain a copyright notice

#ifndef ROSBRIDGE_TEST_MSGS__MSG__DETAIL__TEST_HEADER__TRAITS_HPP_
#define ROSBRIDGE_TEST_MSGS__MSG__DETAIL__TEST_HEADER__TRAITS_HPP_

#include "rosbridge_test_msgs/msg/detail/test_header__struct.hpp"
#include <rosidl_runtime_cpp/traits.hpp>
#include <stdint.h>
#include <type_traits>

// Include directives for member types
// Member 'header'
#include "std_msgs/msg/detail/header__traits.hpp"

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<rosbridge_test_msgs::msg::TestHeader>()
{
  return "rosbridge_test_msgs::msg::TestHeader";
}

template<>
inline const char * name<rosbridge_test_msgs::msg::TestHeader>()
{
  return "rosbridge_test_msgs/msg/TestHeader";
}

template<>
struct has_fixed_size<rosbridge_test_msgs::msg::TestHeader>
  : std::integral_constant<bool, has_fixed_size<std_msgs::msg::Header>::value> {};

template<>
struct has_bounded_size<rosbridge_test_msgs::msg::TestHeader>
  : std::integral_constant<bool, has_bounded_size<std_msgs::msg::Header>::value> {};

template<>
struct is_message<rosbridge_test_msgs::msg::TestHeader>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // ROSBRIDGE_TEST_MSGS__MSG__DETAIL__TEST_HEADER__TRAITS_HPP_
