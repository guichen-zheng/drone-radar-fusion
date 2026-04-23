// generated from rosidl_typesupport_introspection_cpp/resource/idl__type_support.cpp.em
// with input from interface:msg/DroneDetectArray.idl
// generated code does not contain a copyright notice

#include "array"
#include "cstddef"
#include "string"
#include "vector"
#include "rosidl_runtime_c/message_type_support_struct.h"
#include "rosidl_typesupport_cpp/message_type_support.hpp"
#include "rosidl_typesupport_interface/macros.h"
#include "interface/msg/detail/drone_detect_array__struct.hpp"
#include "rosidl_typesupport_introspection_cpp/field_types.hpp"
#include "rosidl_typesupport_introspection_cpp/identifier.hpp"
#include "rosidl_typesupport_introspection_cpp/message_introspection.hpp"
#include "rosidl_typesupport_introspection_cpp/message_type_support_decl.hpp"
#include "rosidl_typesupport_introspection_cpp/visibility_control.h"

namespace interface
{

namespace msg
{

namespace rosidl_typesupport_introspection_cpp
{

void DroneDetectArray_init_function(
  void * message_memory, rosidl_runtime_cpp::MessageInitialization _init)
{
  new (message_memory) interface::msg::DroneDetectArray(_init);
}

void DroneDetectArray_fini_function(void * message_memory)
{
  auto typed_message = static_cast<interface::msg::DroneDetectArray *>(message_memory);
  typed_message->~DroneDetectArray();
}

size_t size_function__DroneDetectArray__drones(const void * untyped_member)
{
  const auto * member = reinterpret_cast<const std::vector<interface::msg::DroneDetect> *>(untyped_member);
  return member->size();
}

const void * get_const_function__DroneDetectArray__drones(const void * untyped_member, size_t index)
{
  const auto & member =
    *reinterpret_cast<const std::vector<interface::msg::DroneDetect> *>(untyped_member);
  return &member[index];
}

void * get_function__DroneDetectArray__drones(void * untyped_member, size_t index)
{
  auto & member =
    *reinterpret_cast<std::vector<interface::msg::DroneDetect> *>(untyped_member);
  return &member[index];
}

void fetch_function__DroneDetectArray__drones(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const auto & item = *reinterpret_cast<const interface::msg::DroneDetect *>(
    get_const_function__DroneDetectArray__drones(untyped_member, index));
  auto & value = *reinterpret_cast<interface::msg::DroneDetect *>(untyped_value);
  value = item;
}

void assign_function__DroneDetectArray__drones(
  void * untyped_member, size_t index, const void * untyped_value)
{
  auto & item = *reinterpret_cast<interface::msg::DroneDetect *>(
    get_function__DroneDetectArray__drones(untyped_member, index));
  const auto & value = *reinterpret_cast<const interface::msg::DroneDetect *>(untyped_value);
  item = value;
}

void resize_function__DroneDetectArray__drones(void * untyped_member, size_t size)
{
  auto * member =
    reinterpret_cast<std::vector<interface::msg::DroneDetect> *>(untyped_member);
  member->resize(size);
}

static const ::rosidl_typesupport_introspection_cpp::MessageMember DroneDetectArray_message_member_array[2] = {
  {
    "header",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    ::rosidl_typesupport_introspection_cpp::get_message_type_support_handle<std_msgs::msg::Header>(),  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(interface::msg::DroneDetectArray, header),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  },
  {
    "drones",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    ::rosidl_typesupport_introspection_cpp::get_message_type_support_handle<interface::msg::DroneDetect>(),  // members of sub message
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(interface::msg::DroneDetectArray, drones),  // bytes offset in struct
    nullptr,  // default value
    size_function__DroneDetectArray__drones,  // size() function pointer
    get_const_function__DroneDetectArray__drones,  // get_const(index) function pointer
    get_function__DroneDetectArray__drones,  // get(index) function pointer
    fetch_function__DroneDetectArray__drones,  // fetch(index, &value) function pointer
    assign_function__DroneDetectArray__drones,  // assign(index, value) function pointer
    resize_function__DroneDetectArray__drones  // resize(index) function pointer
  }
};

static const ::rosidl_typesupport_introspection_cpp::MessageMembers DroneDetectArray_message_members = {
  "interface::msg",  // message namespace
  "DroneDetectArray",  // message name
  2,  // number of fields
  sizeof(interface::msg::DroneDetectArray),
  DroneDetectArray_message_member_array,  // message members
  DroneDetectArray_init_function,  // function to initialize message memory (memory has to be allocated)
  DroneDetectArray_fini_function  // function to terminate message instance (will not free memory)
};

static const rosidl_message_type_support_t DroneDetectArray_message_type_support_handle = {
  ::rosidl_typesupport_introspection_cpp::typesupport_identifier,
  &DroneDetectArray_message_members,
  get_message_typesupport_handle_function,
};

}  // namespace rosidl_typesupport_introspection_cpp

}  // namespace msg

}  // namespace interface


namespace rosidl_typesupport_introspection_cpp
{

template<>
ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_message_type_support_t *
get_message_type_support_handle<interface::msg::DroneDetectArray>()
{
  return &::interface::msg::rosidl_typesupport_introspection_cpp::DroneDetectArray_message_type_support_handle;
}

}  // namespace rosidl_typesupport_introspection_cpp

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_cpp, interface, msg, DroneDetectArray)() {
  return &::interface::msg::rosidl_typesupport_introspection_cpp::DroneDetectArray_message_type_support_handle;
}

#ifdef __cplusplus
}
#endif
