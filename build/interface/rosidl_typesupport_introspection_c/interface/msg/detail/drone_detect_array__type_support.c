// generated from rosidl_typesupport_introspection_c/resource/idl__type_support.c.em
// with input from interface:msg/DroneDetectArray.idl
// generated code does not contain a copyright notice

#include <stddef.h>
#include "interface/msg/detail/drone_detect_array__rosidl_typesupport_introspection_c.h"
#include "interface/msg/rosidl_typesupport_introspection_c__visibility_control.h"
#include "rosidl_typesupport_introspection_c/field_types.h"
#include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/message_introspection.h"
#include "interface/msg/detail/drone_detect_array__functions.h"
#include "interface/msg/detail/drone_detect_array__struct.h"


// Include directives for member types
// Member `header`
#include "std_msgs/msg/header.h"
// Member `header`
#include "std_msgs/msg/detail/header__rosidl_typesupport_introspection_c.h"
// Member `drones`
#include "interface/msg/drone_detect.h"
// Member `drones`
#include "interface/msg/detail/drone_detect__rosidl_typesupport_introspection_c.h"

#ifdef __cplusplus
extern "C"
{
#endif

void interface__msg__DroneDetectArray__rosidl_typesupport_introspection_c__DroneDetectArray_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  interface__msg__DroneDetectArray__init(message_memory);
}

void interface__msg__DroneDetectArray__rosidl_typesupport_introspection_c__DroneDetectArray_fini_function(void * message_memory)
{
  interface__msg__DroneDetectArray__fini(message_memory);
}

size_t interface__msg__DroneDetectArray__rosidl_typesupport_introspection_c__size_function__DroneDetectArray__drones(
  const void * untyped_member)
{
  const interface__msg__DroneDetect__Sequence * member =
    (const interface__msg__DroneDetect__Sequence *)(untyped_member);
  return member->size;
}

const void * interface__msg__DroneDetectArray__rosidl_typesupport_introspection_c__get_const_function__DroneDetectArray__drones(
  const void * untyped_member, size_t index)
{
  const interface__msg__DroneDetect__Sequence * member =
    (const interface__msg__DroneDetect__Sequence *)(untyped_member);
  return &member->data[index];
}

void * interface__msg__DroneDetectArray__rosidl_typesupport_introspection_c__get_function__DroneDetectArray__drones(
  void * untyped_member, size_t index)
{
  interface__msg__DroneDetect__Sequence * member =
    (interface__msg__DroneDetect__Sequence *)(untyped_member);
  return &member->data[index];
}

void interface__msg__DroneDetectArray__rosidl_typesupport_introspection_c__fetch_function__DroneDetectArray__drones(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const interface__msg__DroneDetect * item =
    ((const interface__msg__DroneDetect *)
    interface__msg__DroneDetectArray__rosidl_typesupport_introspection_c__get_const_function__DroneDetectArray__drones(untyped_member, index));
  interface__msg__DroneDetect * value =
    (interface__msg__DroneDetect *)(untyped_value);
  *value = *item;
}

void interface__msg__DroneDetectArray__rosidl_typesupport_introspection_c__assign_function__DroneDetectArray__drones(
  void * untyped_member, size_t index, const void * untyped_value)
{
  interface__msg__DroneDetect * item =
    ((interface__msg__DroneDetect *)
    interface__msg__DroneDetectArray__rosidl_typesupport_introspection_c__get_function__DroneDetectArray__drones(untyped_member, index));
  const interface__msg__DroneDetect * value =
    (const interface__msg__DroneDetect *)(untyped_value);
  *item = *value;
}

bool interface__msg__DroneDetectArray__rosidl_typesupport_introspection_c__resize_function__DroneDetectArray__drones(
  void * untyped_member, size_t size)
{
  interface__msg__DroneDetect__Sequence * member =
    (interface__msg__DroneDetect__Sequence *)(untyped_member);
  interface__msg__DroneDetect__Sequence__fini(member);
  return interface__msg__DroneDetect__Sequence__init(member, size);
}

static rosidl_typesupport_introspection_c__MessageMember interface__msg__DroneDetectArray__rosidl_typesupport_introspection_c__DroneDetectArray_message_member_array[2] = {
  {
    "header",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(interface__msg__DroneDetectArray, header),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "drones",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(interface__msg__DroneDetectArray, drones),  // bytes offset in struct
    NULL,  // default value
    interface__msg__DroneDetectArray__rosidl_typesupport_introspection_c__size_function__DroneDetectArray__drones,  // size() function pointer
    interface__msg__DroneDetectArray__rosidl_typesupport_introspection_c__get_const_function__DroneDetectArray__drones,  // get_const(index) function pointer
    interface__msg__DroneDetectArray__rosidl_typesupport_introspection_c__get_function__DroneDetectArray__drones,  // get(index) function pointer
    interface__msg__DroneDetectArray__rosidl_typesupport_introspection_c__fetch_function__DroneDetectArray__drones,  // fetch(index, &value) function pointer
    interface__msg__DroneDetectArray__rosidl_typesupport_introspection_c__assign_function__DroneDetectArray__drones,  // assign(index, value) function pointer
    interface__msg__DroneDetectArray__rosidl_typesupport_introspection_c__resize_function__DroneDetectArray__drones  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers interface__msg__DroneDetectArray__rosidl_typesupport_introspection_c__DroneDetectArray_message_members = {
  "interface__msg",  // message namespace
  "DroneDetectArray",  // message name
  2,  // number of fields
  sizeof(interface__msg__DroneDetectArray),
  interface__msg__DroneDetectArray__rosidl_typesupport_introspection_c__DroneDetectArray_message_member_array,  // message members
  interface__msg__DroneDetectArray__rosidl_typesupport_introspection_c__DroneDetectArray_init_function,  // function to initialize message memory (memory has to be allocated)
  interface__msg__DroneDetectArray__rosidl_typesupport_introspection_c__DroneDetectArray_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t interface__msg__DroneDetectArray__rosidl_typesupport_introspection_c__DroneDetectArray_message_type_support_handle = {
  0,
  &interface__msg__DroneDetectArray__rosidl_typesupport_introspection_c__DroneDetectArray_message_members,
  get_message_typesupport_handle_function,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_interface
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, interface, msg, DroneDetectArray)() {
  interface__msg__DroneDetectArray__rosidl_typesupport_introspection_c__DroneDetectArray_message_member_array[0].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, std_msgs, msg, Header)();
  interface__msg__DroneDetectArray__rosidl_typesupport_introspection_c__DroneDetectArray_message_member_array[1].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, interface, msg, DroneDetect)();
  if (!interface__msg__DroneDetectArray__rosidl_typesupport_introspection_c__DroneDetectArray_message_type_support_handle.typesupport_identifier) {
    interface__msg__DroneDetectArray__rosidl_typesupport_introspection_c__DroneDetectArray_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &interface__msg__DroneDetectArray__rosidl_typesupport_introspection_c__DroneDetectArray_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif
