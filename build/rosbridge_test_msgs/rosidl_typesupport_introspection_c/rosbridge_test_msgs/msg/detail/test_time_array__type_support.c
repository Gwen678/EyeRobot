// generated from rosidl_typesupport_introspection_c/resource/idl__type_support.c.em
// with input from rosbridge_test_msgs:msg/TestTimeArray.idl
// generated code does not contain a copyright notice

#include <stddef.h>
#include "rosbridge_test_msgs/msg/detail/test_time_array__rosidl_typesupport_introspection_c.h"
#include "rosbridge_test_msgs/msg/rosidl_typesupport_introspection_c__visibility_control.h"
#include "rosidl_typesupport_introspection_c/field_types.h"
#include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/message_introspection.h"
#include "rosbridge_test_msgs/msg/detail/test_time_array__functions.h"
#include "rosbridge_test_msgs/msg/detail/test_time_array__struct.h"


// Include directives for member types
// Member `times`
#include "builtin_interfaces/msg/time.h"
// Member `times`
#include "builtin_interfaces/msg/detail/time__rosidl_typesupport_introspection_c.h"

#ifdef __cplusplus
extern "C"
{
#endif

void TestTimeArray__rosidl_typesupport_introspection_c__TestTimeArray_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  rosbridge_test_msgs__msg__TestTimeArray__init(message_memory);
}

void TestTimeArray__rosidl_typesupport_introspection_c__TestTimeArray_fini_function(void * message_memory)
{
  rosbridge_test_msgs__msg__TestTimeArray__fini(message_memory);
}

size_t TestTimeArray__rosidl_typesupport_introspection_c__size_function__Time__times(
  const void * untyped_member)
{
  const builtin_interfaces__msg__Time__Sequence * member =
    (const builtin_interfaces__msg__Time__Sequence *)(untyped_member);
  return member->size;
}

const void * TestTimeArray__rosidl_typesupport_introspection_c__get_const_function__Time__times(
  const void * untyped_member, size_t index)
{
  const builtin_interfaces__msg__Time__Sequence * member =
    (const builtin_interfaces__msg__Time__Sequence *)(untyped_member);
  return &member->data[index];
}

void * TestTimeArray__rosidl_typesupport_introspection_c__get_function__Time__times(
  void * untyped_member, size_t index)
{
  builtin_interfaces__msg__Time__Sequence * member =
    (builtin_interfaces__msg__Time__Sequence *)(untyped_member);
  return &member->data[index];
}

bool TestTimeArray__rosidl_typesupport_introspection_c__resize_function__Time__times(
  void * untyped_member, size_t size)
{
  builtin_interfaces__msg__Time__Sequence * member =
    (builtin_interfaces__msg__Time__Sequence *)(untyped_member);
  builtin_interfaces__msg__Time__Sequence__fini(member);
  return builtin_interfaces__msg__Time__Sequence__init(member, size);
}

static rosidl_typesupport_introspection_c__MessageMember TestTimeArray__rosidl_typesupport_introspection_c__TestTimeArray_message_member_array[1] = {
  {
    "times",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(rosbridge_test_msgs__msg__TestTimeArray, times),  // bytes offset in struct
    NULL,  // default value
    TestTimeArray__rosidl_typesupport_introspection_c__size_function__Time__times,  // size() function pointer
    TestTimeArray__rosidl_typesupport_introspection_c__get_const_function__Time__times,  // get_const(index) function pointer
    TestTimeArray__rosidl_typesupport_introspection_c__get_function__Time__times,  // get(index) function pointer
    TestTimeArray__rosidl_typesupport_introspection_c__resize_function__Time__times  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers TestTimeArray__rosidl_typesupport_introspection_c__TestTimeArray_message_members = {
  "rosbridge_test_msgs__msg",  // message namespace
  "TestTimeArray",  // message name
  1,  // number of fields
  sizeof(rosbridge_test_msgs__msg__TestTimeArray),
  TestTimeArray__rosidl_typesupport_introspection_c__TestTimeArray_message_member_array,  // message members
  TestTimeArray__rosidl_typesupport_introspection_c__TestTimeArray_init_function,  // function to initialize message memory (memory has to be allocated)
  TestTimeArray__rosidl_typesupport_introspection_c__TestTimeArray_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t TestTimeArray__rosidl_typesupport_introspection_c__TestTimeArray_message_type_support_handle = {
  0,
  &TestTimeArray__rosidl_typesupport_introspection_c__TestTimeArray_message_members,
  get_message_typesupport_handle_function,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_rosbridge_test_msgs
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, rosbridge_test_msgs, msg, TestTimeArray)() {
  TestTimeArray__rosidl_typesupport_introspection_c__TestTimeArray_message_member_array[0].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, builtin_interfaces, msg, Time)();
  if (!TestTimeArray__rosidl_typesupport_introspection_c__TestTimeArray_message_type_support_handle.typesupport_identifier) {
    TestTimeArray__rosidl_typesupport_introspection_c__TestTimeArray_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &TestTimeArray__rosidl_typesupport_introspection_c__TestTimeArray_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif
