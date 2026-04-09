// generated from rosidl_typesupport_fastrtps_c/resource/idl__type_support_c.cpp.em
// with input from rosbridge_msgs:msg/ConnectedClients.idl
// generated code does not contain a copyright notice
#include "rosbridge_msgs/msg/detail/connected_clients__rosidl_typesupport_fastrtps_c.h"


#include <cassert>
#include <limits>
#include <string>
#include "rosidl_typesupport_fastrtps_c/identifier.h"
#include "rosidl_typesupport_fastrtps_c/wstring_conversion.hpp"
#include "rosidl_typesupport_fastrtps_cpp/message_type_support.h"
#include "rosbridge_msgs/msg/rosidl_typesupport_fastrtps_c__visibility_control.h"
#include "rosbridge_msgs/msg/detail/connected_clients__struct.h"
#include "rosbridge_msgs/msg/detail/connected_clients__functions.h"
#include "fastcdr/Cdr.h"

#ifndef _WIN32
# pragma GCC diagnostic push
# pragma GCC diagnostic ignored "-Wunused-parameter"
# ifdef __clang__
#  pragma clang diagnostic ignored "-Wdeprecated-register"
#  pragma clang diagnostic ignored "-Wreturn-type-c-linkage"
# endif
#endif
#ifndef _WIN32
# pragma GCC diagnostic pop
#endif

// includes and forward declarations of message dependencies and their conversion functions

#if defined(__cplusplus)
extern "C"
{
#endif

#include "rosbridge_msgs/msg/detail/connected_client__functions.h"  // clients

// forward declare type support functions
size_t get_serialized_size_rosbridge_msgs__msg__ConnectedClient(
  const void * untyped_ros_message,
  size_t current_alignment);

size_t max_serialized_size_rosbridge_msgs__msg__ConnectedClient(
  bool & full_bounded,
  size_t current_alignment);

const rosidl_message_type_support_t *
  ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, rosbridge_msgs, msg, ConnectedClient)();


using _ConnectedClients__ros_msg_type = rosbridge_msgs__msg__ConnectedClients;

static bool _ConnectedClients__cdr_serialize(
  const void * untyped_ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  if (!untyped_ros_message) {
    fprintf(stderr, "ros message handle is null\n");
    return false;
  }
  const _ConnectedClients__ros_msg_type * ros_message = static_cast<const _ConnectedClients__ros_msg_type *>(untyped_ros_message);
  // Field name: clients
  {
    const message_type_support_callbacks_t * callbacks =
      static_cast<const message_type_support_callbacks_t *>(
      ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(
        rosidl_typesupport_fastrtps_c, rosbridge_msgs, msg, ConnectedClient
      )()->data);
    size_t size = ros_message->clients.size;
    auto array_ptr = ros_message->clients.data;
    cdr << static_cast<uint32_t>(size);
    for (size_t i = 0; i < size; ++i) {
      if (!callbacks->cdr_serialize(
          &array_ptr[i], cdr))
      {
        return false;
      }
    }
  }

  return true;
}

static bool _ConnectedClients__cdr_deserialize(
  eprosima::fastcdr::Cdr & cdr,
  void * untyped_ros_message)
{
  if (!untyped_ros_message) {
    fprintf(stderr, "ros message handle is null\n");
    return false;
  }
  _ConnectedClients__ros_msg_type * ros_message = static_cast<_ConnectedClients__ros_msg_type *>(untyped_ros_message);
  // Field name: clients
  {
    const message_type_support_callbacks_t * callbacks =
      static_cast<const message_type_support_callbacks_t *>(
      ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(
        rosidl_typesupport_fastrtps_c, rosbridge_msgs, msg, ConnectedClient
      )()->data);
    uint32_t cdrSize;
    cdr >> cdrSize;
    size_t size = static_cast<size_t>(cdrSize);
    if (ros_message->clients.data) {
      rosbridge_msgs__msg__ConnectedClient__Sequence__fini(&ros_message->clients);
    }
    if (!rosbridge_msgs__msg__ConnectedClient__Sequence__init(&ros_message->clients, size)) {
      return "failed to create array for field 'clients'";
    }
    auto array_ptr = ros_message->clients.data;
    for (size_t i = 0; i < size; ++i) {
      if (!callbacks->cdr_deserialize(
          cdr, &array_ptr[i]))
      {
        return false;
      }
    }
  }

  return true;
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_rosbridge_msgs
size_t get_serialized_size_rosbridge_msgs__msg__ConnectedClients(
  const void * untyped_ros_message,
  size_t current_alignment)
{
  const _ConnectedClients__ros_msg_type * ros_message = static_cast<const _ConnectedClients__ros_msg_type *>(untyped_ros_message);
  (void)ros_message;
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  (void)padding;
  (void)wchar_size;

  // field.name clients
  {
    size_t array_size = ros_message->clients.size;
    auto array_ptr = ros_message->clients.data;
    current_alignment += padding +
      eprosima::fastcdr::Cdr::alignment(current_alignment, padding);

    for (size_t index = 0; index < array_size; ++index) {
      current_alignment += get_serialized_size_rosbridge_msgs__msg__ConnectedClient(
        &array_ptr[index], current_alignment);
    }
  }

  return current_alignment - initial_alignment;
}

static uint32_t _ConnectedClients__get_serialized_size(const void * untyped_ros_message)
{
  return static_cast<uint32_t>(
    get_serialized_size_rosbridge_msgs__msg__ConnectedClients(
      untyped_ros_message, 0));
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_rosbridge_msgs
size_t max_serialized_size_rosbridge_msgs__msg__ConnectedClients(
  bool & full_bounded,
  size_t current_alignment)
{
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  (void)padding;
  (void)wchar_size;
  (void)full_bounded;

  // member: clients
  {
    size_t array_size = 0;
    full_bounded = false;
    current_alignment += padding +
      eprosima::fastcdr::Cdr::alignment(current_alignment, padding);


    for (size_t index = 0; index < array_size; ++index) {
      current_alignment +=
        max_serialized_size_rosbridge_msgs__msg__ConnectedClient(
        full_bounded, current_alignment);
    }
  }

  return current_alignment - initial_alignment;
}

static size_t _ConnectedClients__max_serialized_size(bool & full_bounded)
{
  return max_serialized_size_rosbridge_msgs__msg__ConnectedClients(
    full_bounded, 0);
}


static message_type_support_callbacks_t __callbacks_ConnectedClients = {
  "rosbridge_msgs::msg",
  "ConnectedClients",
  _ConnectedClients__cdr_serialize,
  _ConnectedClients__cdr_deserialize,
  _ConnectedClients__get_serialized_size,
  _ConnectedClients__max_serialized_size
};

static rosidl_message_type_support_t _ConnectedClients__type_support = {
  rosidl_typesupport_fastrtps_c__identifier,
  &__callbacks_ConnectedClients,
  get_message_typesupport_handle_function,
};

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, rosbridge_msgs, msg, ConnectedClients)() {
  return &_ConnectedClients__type_support;
}

#if defined(__cplusplus)
}
#endif
