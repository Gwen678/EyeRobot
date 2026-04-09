// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from rosbridge_test_msgs:srv/AddTwoInts.idl
// generated code does not contain a copyright notice

#ifndef ROSBRIDGE_TEST_MSGS__SRV__DETAIL__ADD_TWO_INTS__TRAITS_HPP_
#define ROSBRIDGE_TEST_MSGS__SRV__DETAIL__ADD_TWO_INTS__TRAITS_HPP_

#include "rosbridge_test_msgs/srv/detail/add_two_ints__struct.hpp"
#include <rosidl_runtime_cpp/traits.hpp>
#include <stdint.h>
#include <type_traits>

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<rosbridge_test_msgs::srv::AddTwoInts_Request>()
{
  return "rosbridge_test_msgs::srv::AddTwoInts_Request";
}

template<>
inline const char * name<rosbridge_test_msgs::srv::AddTwoInts_Request>()
{
  return "rosbridge_test_msgs/srv/AddTwoInts_Request";
}

template<>
struct has_fixed_size<rosbridge_test_msgs::srv::AddTwoInts_Request>
  : std::integral_constant<bool, true> {};

template<>
struct has_bounded_size<rosbridge_test_msgs::srv::AddTwoInts_Request>
  : std::integral_constant<bool, true> {};

template<>
struct is_message<rosbridge_test_msgs::srv::AddTwoInts_Request>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<rosbridge_test_msgs::srv::AddTwoInts_Response>()
{
  return "rosbridge_test_msgs::srv::AddTwoInts_Response";
}

template<>
inline const char * name<rosbridge_test_msgs::srv::AddTwoInts_Response>()
{
  return "rosbridge_test_msgs/srv/AddTwoInts_Response";
}

template<>
struct has_fixed_size<rosbridge_test_msgs::srv::AddTwoInts_Response>
  : std::integral_constant<bool, true> {};

template<>
struct has_bounded_size<rosbridge_test_msgs::srv::AddTwoInts_Response>
  : std::integral_constant<bool, true> {};

template<>
struct is_message<rosbridge_test_msgs::srv::AddTwoInts_Response>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<rosbridge_test_msgs::srv::AddTwoInts>()
{
  return "rosbridge_test_msgs::srv::AddTwoInts";
}

template<>
inline const char * name<rosbridge_test_msgs::srv::AddTwoInts>()
{
  return "rosbridge_test_msgs/srv/AddTwoInts";
}

template<>
struct has_fixed_size<rosbridge_test_msgs::srv::AddTwoInts>
  : std::integral_constant<
    bool,
    has_fixed_size<rosbridge_test_msgs::srv::AddTwoInts_Request>::value &&
    has_fixed_size<rosbridge_test_msgs::srv::AddTwoInts_Response>::value
  >
{
};

template<>
struct has_bounded_size<rosbridge_test_msgs::srv::AddTwoInts>
  : std::integral_constant<
    bool,
    has_bounded_size<rosbridge_test_msgs::srv::AddTwoInts_Request>::value &&
    has_bounded_size<rosbridge_test_msgs::srv::AddTwoInts_Response>::value
  >
{
};

template<>
struct is_service<rosbridge_test_msgs::srv::AddTwoInts>
  : std::true_type
{
};

template<>
struct is_service_request<rosbridge_test_msgs::srv::AddTwoInts_Request>
  : std::true_type
{
};

template<>
struct is_service_response<rosbridge_test_msgs::srv::AddTwoInts_Response>
  : std::true_type
{
};

}  // namespace rosidl_generator_traits

#endif  // ROSBRIDGE_TEST_MSGS__SRV__DETAIL__ADD_TWO_INTS__TRAITS_HPP_
