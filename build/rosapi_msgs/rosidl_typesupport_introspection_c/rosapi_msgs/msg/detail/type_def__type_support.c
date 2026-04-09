// generated from rosidl_typesupport_introspection_c/resource/idl__type_support.c.em
// with input from rosapi_msgs:msg/TypeDef.idl
// generated code does not contain a copyright notice

#include <stddef.h>
#include "rosapi_msgs/msg/detail/type_def__rosidl_typesupport_introspection_c.h"
#include "rosapi_msgs/msg/rosidl_typesupport_introspection_c__visibility_control.h"
#include "rosidl_typesupport_introspection_c/field_types.h"
#include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/message_introspection.h"
#include "rosapi_msgs/msg/detail/type_def__functions.h"
#include "rosapi_msgs/msg/detail/type_def__struct.h"


// Include directives for member types
// Member `type`
// Member `fieldnames`
// Member `fieldtypes`
// Member `examples`
// Member `constnames`
// Member `constvalues`
#include "rosidl_runtime_c/string_functions.h"
// Member `fieldarraylen`
#include "rosidl_runtime_c/primitives_sequence_functions.h"

#ifdef __cplusplus
extern "C"
{
#endif

void TypeDef__rosidl_typesupport_introspection_c__TypeDef_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  rosapi_msgs__msg__TypeDef__init(message_memory);
}

void TypeDef__rosidl_typesupport_introspection_c__TypeDef_fini_function(void * message_memory)
{
  rosapi_msgs__msg__TypeDef__fini(message_memory);
}

static rosidl_typesupport_introspection_c__MessageMember TypeDef__rosidl_typesupport_introspection_c__TypeDef_message_member_array[7] = {
  {
    "type",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_STRING,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(rosapi_msgs__msg__TypeDef, type),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "fieldnames",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_STRING,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(rosapi_msgs__msg__TypeDef, fieldnames),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "fieldtypes",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_STRING,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(rosapi_msgs__msg__TypeDef, fieldtypes),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "fieldarraylen",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_INT32,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(rosapi_msgs__msg__TypeDef, fieldarraylen),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "examples",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_STRING,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(rosapi_msgs__msg__TypeDef, examples),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "constnames",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_STRING,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(rosapi_msgs__msg__TypeDef, constnames),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "constvalues",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_STRING,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(rosapi_msgs__msg__TypeDef, constvalues),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers TypeDef__rosidl_typesupport_introspection_c__TypeDef_message_members = {
  "rosapi_msgs__msg",  // message namespace
  "TypeDef",  // message name
  7,  // number of fields
  sizeof(rosapi_msgs__msg__TypeDef),
  TypeDef__rosidl_typesupport_introspection_c__TypeDef_message_member_array,  // message members
  TypeDef__rosidl_typesupport_introspection_c__TypeDef_init_function,  // function to initialize message memory (memory has to be allocated)
  TypeDef__rosidl_typesupport_introspection_c__TypeDef_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t TypeDef__rosidl_typesupport_introspection_c__TypeDef_message_type_support_handle = {
  0,
  &TypeDef__rosidl_typesupport_introspection_c__TypeDef_message_members,
  get_message_typesupport_handle_function,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_rosapi_msgs
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, rosapi_msgs, msg, TypeDef)() {
  if (!TypeDef__rosidl_typesupport_introspection_c__TypeDef_message_type_support_handle.typesupport_identifier) {
    TypeDef__rosidl_typesupport_introspection_c__TypeDef_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &TypeDef__rosidl_typesupport_introspection_c__TypeDef_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif
