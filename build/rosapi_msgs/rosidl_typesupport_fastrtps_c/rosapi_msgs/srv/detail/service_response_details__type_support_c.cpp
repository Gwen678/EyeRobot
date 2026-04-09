// generated from rosidl_typesupport_fastrtps_c/resource/idl__type_support_c.cpp.em
// with input from rosapi_msgs:srv/ServiceResponseDetails.idl
// generated code does not contain a copyright notice
#include "rosapi_msgs/srv/detail/service_response_details__rosidl_typesupport_fastrtps_c.h"


#include <cassert>
#include <limits>
#include <string>
#include "rosidl_typesupport_fastrtps_c/identifier.h"
#include "rosidl_typesupport_fastrtps_c/wstring_conversion.hpp"
#include "rosidl_typesupport_fastrtps_cpp/message_type_support.h"
#include "rosapi_msgs/msg/rosidl_typesupport_fastrtps_c__visibility_control.h"
#include "rosapi_msgs/srv/detail/service_response_details__struct.h"
#include "rosapi_msgs/srv/detail/service_response_details__functions.h"
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

#include "rosidl_runtime_c/string.h"  // type
#include "rosidl_runtime_c/string_functions.h"  // type

// forward declare type support functions


using _ServiceResponseDetails_Request__ros_msg_type = rosapi_msgs__srv__ServiceResponseDetails_Request;

static bool _ServiceResponseDetails_Request__cdr_serialize(
  const void * untyped_ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  if (!untyped_ros_message) {
    fprintf(stderr, "ros message handle is null\n");
    return false;
  }
  const _ServiceResponseDetails_Request__ros_msg_type * ros_message = static_cast<const _ServiceResponseDetails_Request__ros_msg_type *>(untyped_ros_message);
  // Field name: type
  {
    const rosidl_runtime_c__String * str = &ros_message->type;
    if (str->capacity == 0 || str->capacity <= str->size) {
      fprintf(stderr, "string capacity not greater than size\n");
      return false;
    }
    if (str->data[str->size] != '\0') {
      fprintf(stderr, "string not null-terminated\n");
      return false;
    }
    cdr << str->data;
  }

  return true;
}

static bool _ServiceResponseDetails_Request__cdr_deserialize(
  eprosima::fastcdr::Cdr & cdr,
  void * untyped_ros_message)
{
  if (!untyped_ros_message) {
    fprintf(stderr, "ros message handle is null\n");
    return false;
  }
  _ServiceResponseDetails_Request__ros_msg_type * ros_message = static_cast<_ServiceResponseDetails_Request__ros_msg_type *>(untyped_ros_message);
  // Field name: type
  {
    std::string tmp;
    cdr >> tmp;
    if (!ros_message->type.data) {
      rosidl_runtime_c__String__init(&ros_message->type);
    }
    bool succeeded = rosidl_runtime_c__String__assign(
      &ros_message->type,
      tmp.c_str());
    if (!succeeded) {
      fprintf(stderr, "failed to assign string into field 'type'\n");
      return false;
    }
  }

  return true;
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_rosapi_msgs
size_t get_serialized_size_rosapi_msgs__srv__ServiceResponseDetails_Request(
  const void * untyped_ros_message,
  size_t current_alignment)
{
  const _ServiceResponseDetails_Request__ros_msg_type * ros_message = static_cast<const _ServiceResponseDetails_Request__ros_msg_type *>(untyped_ros_message);
  (void)ros_message;
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  (void)padding;
  (void)wchar_size;

  // field.name type
  current_alignment += padding +
    eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
    (ros_message->type.size + 1);

  return current_alignment - initial_alignment;
}

static uint32_t _ServiceResponseDetails_Request__get_serialized_size(const void * untyped_ros_message)
{
  return static_cast<uint32_t>(
    get_serialized_size_rosapi_msgs__srv__ServiceResponseDetails_Request(
      untyped_ros_message, 0));
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_rosapi_msgs
size_t max_serialized_size_rosapi_msgs__srv__ServiceResponseDetails_Request(
  bool & full_bounded,
  size_t current_alignment)
{
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  (void)padding;
  (void)wchar_size;
  (void)full_bounded;

  // member: type
  {
    size_t array_size = 1;

    full_bounded = false;
    for (size_t index = 0; index < array_size; ++index) {
      current_alignment += padding +
        eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
        1;
    }
  }

  return current_alignment - initial_alignment;
}

static size_t _ServiceResponseDetails_Request__max_serialized_size(bool & full_bounded)
{
  return max_serialized_size_rosapi_msgs__srv__ServiceResponseDetails_Request(
    full_bounded, 0);
}


static message_type_support_callbacks_t __callbacks_ServiceResponseDetails_Request = {
  "rosapi_msgs::srv",
  "ServiceResponseDetails_Request",
  _ServiceResponseDetails_Request__cdr_serialize,
  _ServiceResponseDetails_Request__cdr_deserialize,
  _ServiceResponseDetails_Request__get_serialized_size,
  _ServiceResponseDetails_Request__max_serialized_size
};

static rosidl_message_type_support_t _ServiceResponseDetails_Request__type_support = {
  rosidl_typesupport_fastrtps_c__identifier,
  &__callbacks_ServiceResponseDetails_Request,
  get_message_typesupport_handle_function,
};

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, rosapi_msgs, srv, ServiceResponseDetails_Request)() {
  return &_ServiceResponseDetails_Request__type_support;
}

#if defined(__cplusplus)
}
#endif

// already included above
// #include <cassert>
// already included above
// #include <limits>
// already included above
// #include <string>
// already included above
// #include "rosidl_typesupport_fastrtps_c/identifier.h"
// already included above
// #include "rosidl_typesupport_fastrtps_c/wstring_conversion.hpp"
// already included above
// #include "rosidl_typesupport_fastrtps_cpp/message_type_support.h"
// already included above
// #include "rosapi_msgs/msg/rosidl_typesupport_fastrtps_c__visibility_control.h"
// already included above
// #include "rosapi_msgs/srv/detail/service_response_details__struct.h"
// already included above
// #include "rosapi_msgs/srv/detail/service_response_details__functions.h"
// already included above
// #include "fastcdr/Cdr.h"

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

#include "rosapi_msgs/msg/detail/type_def__functions.h"  // typedefs

// forward declare type support functions
size_t get_serialized_size_rosapi_msgs__msg__TypeDef(
  const void * untyped_ros_message,
  size_t current_alignment);

size_t max_serialized_size_rosapi_msgs__msg__TypeDef(
  bool & full_bounded,
  size_t current_alignment);

const rosidl_message_type_support_t *
  ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, rosapi_msgs, msg, TypeDef)();


using _ServiceResponseDetails_Response__ros_msg_type = rosapi_msgs__srv__ServiceResponseDetails_Response;

static bool _ServiceResponseDetails_Response__cdr_serialize(
  const void * untyped_ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  if (!untyped_ros_message) {
    fprintf(stderr, "ros message handle is null\n");
    return false;
  }
  const _ServiceResponseDetails_Response__ros_msg_type * ros_message = static_cast<const _ServiceResponseDetails_Response__ros_msg_type *>(untyped_ros_message);
  // Field name: typedefs
  {
    const message_type_support_callbacks_t * callbacks =
      static_cast<const message_type_support_callbacks_t *>(
      ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(
        rosidl_typesupport_fastrtps_c, rosapi_msgs, msg, TypeDef
      )()->data);
    size_t size = ros_message->typedefs.size;
    auto array_ptr = ros_message->typedefs.data;
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

static bool _ServiceResponseDetails_Response__cdr_deserialize(
  eprosima::fastcdr::Cdr & cdr,
  void * untyped_ros_message)
{
  if (!untyped_ros_message) {
    fprintf(stderr, "ros message handle is null\n");
    return false;
  }
  _ServiceResponseDetails_Response__ros_msg_type * ros_message = static_cast<_ServiceResponseDetails_Response__ros_msg_type *>(untyped_ros_message);
  // Field name: typedefs
  {
    const message_type_support_callbacks_t * callbacks =
      static_cast<const message_type_support_callbacks_t *>(
      ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(
        rosidl_typesupport_fastrtps_c, rosapi_msgs, msg, TypeDef
      )()->data);
    uint32_t cdrSize;
    cdr >> cdrSize;
    size_t size = static_cast<size_t>(cdrSize);
    if (ros_message->typedefs.data) {
      rosapi_msgs__msg__TypeDef__Sequence__fini(&ros_message->typedefs);
    }
    if (!rosapi_msgs__msg__TypeDef__Sequence__init(&ros_message->typedefs, size)) {
      return "failed to create array for field 'typedefs'";
    }
    auto array_ptr = ros_message->typedefs.data;
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

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_rosapi_msgs
size_t get_serialized_size_rosapi_msgs__srv__ServiceResponseDetails_Response(
  const void * untyped_ros_message,
  size_t current_alignment)
{
  const _ServiceResponseDetails_Response__ros_msg_type * ros_message = static_cast<const _ServiceResponseDetails_Response__ros_msg_type *>(untyped_ros_message);
  (void)ros_message;
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  (void)padding;
  (void)wchar_size;

  // field.name typedefs
  {
    size_t array_size = ros_message->typedefs.size;
    auto array_ptr = ros_message->typedefs.data;
    current_alignment += padding +
      eprosima::fastcdr::Cdr::alignment(current_alignment, padding);

    for (size_t index = 0; index < array_size; ++index) {
      current_alignment += get_serialized_size_rosapi_msgs__msg__TypeDef(
        &array_ptr[index], current_alignment);
    }
  }

  return current_alignment - initial_alignment;
}

static uint32_t _ServiceResponseDetails_Response__get_serialized_size(const void * untyped_ros_message)
{
  return static_cast<uint32_t>(
    get_serialized_size_rosapi_msgs__srv__ServiceResponseDetails_Response(
      untyped_ros_message, 0));
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_rosapi_msgs
size_t max_serialized_size_rosapi_msgs__srv__ServiceResponseDetails_Response(
  bool & full_bounded,
  size_t current_alignment)
{
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  (void)padding;
  (void)wchar_size;
  (void)full_bounded;

  // member: typedefs
  {
    size_t array_size = 0;
    full_bounded = false;
    current_alignment += padding +
      eprosima::fastcdr::Cdr::alignment(current_alignment, padding);


    for (size_t index = 0; index < array_size; ++index) {
      current_alignment +=
        max_serialized_size_rosapi_msgs__msg__TypeDef(
        full_bounded, current_alignment);
    }
  }

  return current_alignment - initial_alignment;
}

static size_t _ServiceResponseDetails_Response__max_serialized_size(bool & full_bounded)
{
  return max_serialized_size_rosapi_msgs__srv__ServiceResponseDetails_Response(
    full_bounded, 0);
}


static message_type_support_callbacks_t __callbacks_ServiceResponseDetails_Response = {
  "rosapi_msgs::srv",
  "ServiceResponseDetails_Response",
  _ServiceResponseDetails_Response__cdr_serialize,
  _ServiceResponseDetails_Response__cdr_deserialize,
  _ServiceResponseDetails_Response__get_serialized_size,
  _ServiceResponseDetails_Response__max_serialized_size
};

static rosidl_message_type_support_t _ServiceResponseDetails_Response__type_support = {
  rosidl_typesupport_fastrtps_c__identifier,
  &__callbacks_ServiceResponseDetails_Response,
  get_message_typesupport_handle_function,
};

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, rosapi_msgs, srv, ServiceResponseDetails_Response)() {
  return &_ServiceResponseDetails_Response__type_support;
}

#if defined(__cplusplus)
}
#endif

#include "rosidl_typesupport_fastrtps_cpp/service_type_support.h"
#include "rosidl_typesupport_cpp/service_type_support.hpp"
// already included above
// #include "rosidl_typesupport_fastrtps_c/identifier.h"
// already included above
// #include "rosapi_msgs/msg/rosidl_typesupport_fastrtps_c__visibility_control.h"
#include "rosapi_msgs/srv/service_response_details.h"

#if defined(__cplusplus)
extern "C"
{
#endif

static service_type_support_callbacks_t ServiceResponseDetails__callbacks = {
  "rosapi_msgs::srv",
  "ServiceResponseDetails",
  ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, rosapi_msgs, srv, ServiceResponseDetails_Request)(),
  ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, rosapi_msgs, srv, ServiceResponseDetails_Response)(),
};

static rosidl_service_type_support_t ServiceResponseDetails__handle = {
  rosidl_typesupport_fastrtps_c__identifier,
  &ServiceResponseDetails__callbacks,
  get_service_typesupport_handle_function,
};

const rosidl_service_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__SERVICE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, rosapi_msgs, srv, ServiceResponseDetails)() {
  return &ServiceResponseDetails__handle;
}

#if defined(__cplusplus)
}
#endif
