// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from visualization_msgs:msg/Marker.idl
// generated code does not contain a copyright notice

#ifndef VISUALIZATION_MSGS__MSG__DETAIL__MARKER__STRUCT_H_
#define VISUALIZATION_MSGS__MSG__DETAIL__MARKER__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

/// Constant 'ARROW'.
enum
{
  visualization_msgs__msg__Marker__ARROW = 0l
};

/// Constant 'CUBE'.
enum
{
  visualization_msgs__msg__Marker__CUBE = 1l
};

/// Constant 'SPHERE'.
enum
{
  visualization_msgs__msg__Marker__SPHERE = 2l
};

/// Constant 'CYLINDER'.
enum
{
  visualization_msgs__msg__Marker__CYLINDER = 3l
};

/// Constant 'LINE_STRIP'.
enum
{
  visualization_msgs__msg__Marker__LINE_STRIP = 4l
};

/// Constant 'LINE_LIST'.
enum
{
  visualization_msgs__msg__Marker__LINE_LIST = 5l
};

/// Constant 'CUBE_LIST'.
enum
{
  visualization_msgs__msg__Marker__CUBE_LIST = 6l
};

/// Constant 'SPHERE_LIST'.
enum
{
  visualization_msgs__msg__Marker__SPHERE_LIST = 7l
};

/// Constant 'POINTS'.
enum
{
  visualization_msgs__msg__Marker__POINTS = 8l
};

/// Constant 'TEXT_VIEW_FACING'.
enum
{
  visualization_msgs__msg__Marker__TEXT_VIEW_FACING = 9l
};

/// Constant 'MESH_RESOURCE'.
enum
{
  visualization_msgs__msg__Marker__MESH_RESOURCE = 10l
};

/// Constant 'TRIANGLE_LIST'.
enum
{
  visualization_msgs__msg__Marker__TRIANGLE_LIST = 11l
};

/// Constant 'ADD'.
enum
{
  visualization_msgs__msg__Marker__ADD = 0l
};

/// Constant 'MODIFY'.
enum
{
  visualization_msgs__msg__Marker__MODIFY = 0l
};

/// Constant 'DELETE'.
enum
{
  visualization_msgs__msg__Marker__DELETE = 2l
};

/// Constant 'DELETEALL'.
enum
{
  visualization_msgs__msg__Marker__DELETEALL = 3l
};

// Include directives for member types
// Member 'header'
#include "std_msgs/msg/detail/header__struct.h"
// Member 'ns'
// Member 'text'
// Member 'mesh_resource'
#include "rosidl_runtime_c/string.h"
// Member 'pose'
#include "geometry_msgs/msg/detail/pose__struct.h"
// Member 'scale'
#include "geometry_msgs/msg/detail/vector3__struct.h"
// Member 'color'
// Member 'colors'
#include "std_msgs/msg/detail/color_rgba__struct.h"
// Member 'lifetime'
#include "builtin_interfaces/msg/detail/duration__struct.h"
// Member 'points'
#include "geometry_msgs/msg/detail/point__struct.h"

/// Struct defined in msg/Marker in the package visualization_msgs.
/**
  * See:
  *  - http://www.ros.org/wiki/rviz/DisplayTypes/Marker
  *  - http://www.ros.org/wiki/rviz/Tutorials/Markers%3A%20Basic%20Shapes
  *
  * for more information on using this message with rviz.
 */
typedef struct visualization_msgs__msg__Marker
{
  /// Header for timestamp and frame id.
  std_msgs__msg__Header header;
  /// Namespace in which to place the object.
  /// Used in conjunction with id to create a unique name for the object.
  rosidl_runtime_c__String ns;
  /// Object ID used in conjunction with the namespace for manipulating and deleting the object later.
  int32_t id;
  /// Type of object.
  int32_t type;
  /// Action to take; one of:
  ///  - 0 add/modify an object
  ///  - 1 (deprecated)
  ///  - 2 deletes an object
  ///  - 3 deletes all objects
  int32_t action;
  /// Pose of the object with respect the frame_id specified in the header.
  geometry_msgs__msg__Pose pose;
  /// Scale of the object; 1,1,1 means default (usually 1 meter square).
  geometry_msgs__msg__Vector3 scale;
  /// Color of the object; in the range:
  std_msgs__msg__ColorRGBA color;
  /// How long the object should last before being automatically deleted.
  /// 0 indicates forever.
  builtin_interfaces__msg__Duration lifetime;
  /// If this marker should be frame-locked, i.e. retransformed into its frame every timestep.
  bool frame_locked;
  /// Only used if the type specified has some use for them (eg. POINTS, LINE_STRIP, etc.)
  geometry_msgs__msg__Point__Sequence points;
  /// Only used if the type specified has some use for them (eg. POINTS, LINE_STRIP, etc.)
  /// The number of colors provided must either be 0 or equal to the number of points provided.
  /// NOTE: alpha is not yet used
  std_msgs__msg__ColorRGBA__Sequence colors;
  /// Only used for text markers
  rosidl_runtime_c__String text;
  /// Only used for MESH_RESOURCE markers.
  rosidl_runtime_c__String mesh_resource;
  bool mesh_use_embedded_materials;
} visualization_msgs__msg__Marker;

// Struct for a sequence of visualization_msgs__msg__Marker.
typedef struct visualization_msgs__msg__Marker__Sequence
{
  visualization_msgs__msg__Marker * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} visualization_msgs__msg__Marker__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // VISUALIZATION_MSGS__MSG__DETAIL__MARKER__STRUCT_H_
