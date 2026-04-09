// generated from rosidl_typesupport_introspection_c/resource/idl__type_support.c.em
// with input from rosbridge_msgs:msg/ConnectedClients.idl
// generated code does not contain a copyright notice

#include <stddef.h>
#include "rosbridge_msgs/msg/detail/connected_clients__rosidl_typesupport_introspection_c.h"
#include "rosbridge_msgs/msg/rosidl_typesupport_introspection_c__visibility_control.h"
#include "rosidl_typesupport_introspection_c/field_types.h"
#include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/message_introspection.h"
#include "rosbridge_msgs/msg/detail/connected_clients__functions.h"
#include "rosbridge_msgs/msg/detail/connected_clients__struct.h"


// Include directives for member types
// Member `clients`
#include "rosbridge_msgs/msg/connected_client.h"
// Member `clients`
#include "rosbridge_msgs/msg/detail/connected_client__rosidl_typesupport_introspection_c.h"

#ifdef __cplusplus
extern "C"
{
#endif

void ConnectedClients__rosidl_typesupport_introspection_c__ConnectedClients_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  rosbridge_msgs__msg__ConnectedClients__init(message_memory);
}

void ConnectedClients__rosidl_typesupport_introspection_c__ConnectedClients_fini_function(void * message_memory)
{
  rosbridge_msgs__msg__ConnectedClients__fini(message_memory);
}

size_t ConnectedClients__rosidl_typesupport_introspection_c__size_function__ConnectedClient__clients(
  const void * untyped_member)
{
  const rosbridge_msgs__msg__ConnectedClient__Sequence * member =
    (const rosbridge_msgs__msg__ConnectedClient__Sequence *)(untyped_member);
  return member->size;
}

const void * ConnectedClients__rosidl_typesupport_introspection_c__get_const_function__ConnectedClient__clients(
  const void * untyped_member, size_t index)
{
  const rosbridge_msgs__msg__ConnectedClient__Sequence * member =
    (const rosbridge_msgs__msg__ConnectedClient__Sequence *)(untyped_member);
  return &member->data[index];
}

void * ConnectedClients__rosidl_typesupport_introspection_c__get_function__ConnectedClient__clients(
  void * untyped_member, size_t index)
{
  rosbridge_msgs__msg__ConnectedClient__Sequence * member =
    (rosbridge_msgs__msg__ConnectedClient__Sequence *)(untyped_member);
  return &member->data[index];
}

bool ConnectedClients__rosidl_typesupport_introspection_c__resize_function__ConnectedClient__clients(
  void * untyped_member, size_t size)
{
  rosbridge_msgs__msg__ConnectedClient__Sequence * member =
    (rosbridge_msgs__msg__ConnectedClient__Sequence *)(untyped_member);
  rosbridge_msgs__msg__ConnectedClient__Sequence__fini(member);
  return rosbridge_msgs__msg__ConnectedClient__Sequence__init(member, size);
}

static rosidl_typesupport_introspection_c__MessageMember ConnectedClients__rosidl_typesupport_introspection_c__ConnectedClients_message_member_array[1] = {
  {
    "clients",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(rosbridge_msgs__msg__ConnectedClients, clients),  // bytes offset in struct
    NULL,  // default value
    ConnectedClients__rosidl_typesupport_introspection_c__size_function__ConnectedClient__clients,  // size() function pointer
    ConnectedClients__rosidl_typesupport_introspection_c__get_const_function__ConnectedClient__clients,  // get_const(index) function pointer
    ConnectedClients__rosidl_typesupport_introspection_c__get_function__ConnectedClient__clients,  // get(index) function pointer
    ConnectedClients__rosidl_typesupport_introspection_c__resize_function__ConnectedClient__clients  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers ConnectedClients__rosidl_typesupport_introspection_c__ConnectedClients_message_members = {
  "rosbridge_msgs__msg",  // message namespace
  "ConnectedClients",  // message name
  1,  // number of fields
  sizeof(rosbridge_msgs__msg__ConnectedClients),
  ConnectedClients__rosidl_typesupport_introspection_c__ConnectedClients_message_member_array,  // message members
  ConnectedClients__rosidl_typesupport_introspection_c__ConnectedClients_init_function,  // function to initialize message memory (memory has to be allocated)
  ConnectedClients__rosidl_typesupport_introspection_c__ConnectedClients_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t ConnectedClients__rosidl_typesupport_introspection_c__ConnectedClients_message_type_support_handle = {
  0,
  &ConnectedClients__rosidl_typesupport_introspection_c__ConnectedClients_message_members,
  get_message_typesupport_handle_function,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_rosbridge_msgs
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, rosbridge_msgs, msg, ConnectedClients)() {
  ConnectedClients__rosidl_typesupport_introspection_c__ConnectedClients_message_member_array[0].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, rosbridge_msgs, msg, ConnectedClient)();
  if (!ConnectedClients__rosidl_typesupport_introspection_c__ConnectedClients_message_type_support_handle.typesupport_identifier) {
    ConnectedClients__rosidl_typesupport_introspection_c__ConnectedClients_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &ConnectedClients__rosidl_typesupport_introspection_c__ConnectedClients_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif
