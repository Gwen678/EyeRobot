// generated from rosidl_typesupport_introspection_c/resource/idl__type_support.c.em
// with input from rosbridge_test_msgs:msg/TestDurationArray.idl
// generated code does not contain a copyright notice

#include <stddef.h>
#include "rosbridge_test_msgs/msg/detail/test_duration_array__rosidl_typesupport_introspection_c.h"
#include "rosbridge_test_msgs/msg/rosidl_typesupport_introspection_c__visibility_control.h"
#include "rosidl_typesupport_introspection_c/field_types.h"
#include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/message_introspection.h"
#include "rosbridge_test_msgs/msg/detail/test_duration_array__functions.h"
#include "rosbridge_test_msgs/msg/detail/test_duration_array__struct.h"


// Include directives for member types
// Member `durations`
#include "builtin_interfaces/msg/duration.h"
// Member `durations`
#include "builtin_interfaces/msg/detail/duration__rosidl_typesupport_introspection_c.h"

#ifdef __cplusplus
extern "C"
{
#endif

void TestDurationArray__rosidl_typesupport_introspection_c__TestDurationArray_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  rosbridge_test_msgs__msg__TestDurationArray__init(message_memory);
}

void TestDurationArray__rosidl_typesupport_introspection_c__TestDurationArray_fini_function(void * message_memory)
{
  rosbridge_test_msgs__msg__TestDurationArray__fini(message_memory);
}

size_t TestDurationArray__rosidl_typesupport_introspection_c__size_function__Duration__durations(
  const void * untyped_member)
{
  const builtin_interfaces__msg__Duration__Sequence * member =
    (const builtin_interfaces__msg__Duration__Sequence *)(untyped_member);
  return member->size;
}

const void * TestDurationArray__rosidl_typesupport_introspection_c__get_const_function__Duration__durations(
  const void * untyped_member, size_t index)
{
  const builtin_interfaces__msg__Duration__Sequence * member =
    (const builtin_interfaces__msg__Duration__Sequence *)(untyped_member);
  return &member->data[index];
}

void * TestDurationArray__rosidl_typesupport_introspection_c__get_function__Duration__durations(
  void * untyped_member, size_t index)
{
  builtin_interfaces__msg__Duration__Sequence * member =
    (builtin_interfaces__msg__Duration__Sequence *)(untyped_member);
  return &member->data[index];
}

bool TestDurationArray__rosidl_typesupport_introspection_c__resize_function__Duration__durations(
  void * untyped_member, size_t size)
{
  builtin_interfaces__msg__Duration__Sequence * member =
    (builtin_interfaces__msg__Duration__Sequence *)(untyped_member);
  builtin_interfaces__msg__Duration__Sequence__fini(member);
  return builtin_interfaces__msg__Duration__Sequence__init(member, size);
}

static rosidl_typesupport_introspection_c__MessageMember TestDurationArray__rosidl_typesupport_introspection_c__TestDurationArray_message_member_array[1] = {
  {
    "durations",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(rosbridge_test_msgs__msg__TestDurationArray, durations),  // bytes offset in struct
    NULL,  // default value
    TestDurationArray__rosidl_typesupport_introspection_c__size_function__Duration__durations,  // size() function pointer
    TestDurationArray__rosidl_typesupport_introspection_c__get_const_function__Duration__durations,  // get_const(index) function pointer
    TestDurationArray__rosidl_typesupport_introspection_c__get_function__Duration__durations,  // get(index) function pointer
    TestDurationArray__rosidl_typesupport_introspection_c__resize_function__Duration__durations  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers TestDurationArray__rosidl_typesupport_introspection_c__TestDurationArray_message_members = {
  "rosbridge_test_msgs__msg",  // message namespace
  "TestDurationArray",  // message name
  1,  // number of fields
  sizeof(rosbridge_test_msgs__msg__TestDurationArray),
  TestDurationArray__rosidl_typesupport_introspection_c__TestDurationArray_message_member_array,  // message members
  TestDurationArray__rosidl_typesupport_introspection_c__TestDurationArray_init_function,  // function to initialize message memory (memory has to be allocated)
  TestDurationArray__rosidl_typesupport_introspection_c__TestDurationArray_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t TestDurationArray__rosidl_typesupport_introspection_c__TestDurationArray_message_type_support_handle = {
  0,
  &TestDurationArray__rosidl_typesupport_introspection_c__TestDurationArray_message_members,
  get_message_typesupport_handle_function,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_rosbridge_test_msgs
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, rosbridge_test_msgs, msg, TestDurationArray)() {
  TestDurationArray__rosidl_typesupport_introspection_c__TestDurationArray_message_member_array[0].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, builtin_interfaces, msg, Duration)();
  if (!TestDurationArray__rosidl_typesupport_introspection_c__TestDurationArray_message_type_support_handle.typesupport_identifier) {
    TestDurationArray__rosidl_typesupport_introspection_c__TestDurationArray_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &TestDurationArray__rosidl_typesupport_introspection_c__TestDurationArray_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif
