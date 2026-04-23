// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from interface:msg/RadarWarn.idl
// generated code does not contain a copyright notice
#include "interface/msg/detail/radar_warn__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


// Include directives for member types
// Member `header`
#include "std_msgs/msg/detail/header__functions.h"
// Member `warn_level`
// Member `description`
#include "rosidl_runtime_c/string_functions.h"
// Member `detected_at`
#include "builtin_interfaces/msg/detail/time__functions.h"

bool
interface__msg__RadarWarn__init(interface__msg__RadarWarn * msg)
{
  if (!msg) {
    return false;
  }
  // header
  if (!std_msgs__msg__Header__init(&msg->header)) {
    interface__msg__RadarWarn__fini(msg);
    return false;
  }
  // drone_id
  // x
  // y
  // z
  // confidence
  // warn_level
  if (!rosidl_runtime_c__String__init(&msg->warn_level)) {
    interface__msg__RadarWarn__fini(msg);
    return false;
  }
  // description
  if (!rosidl_runtime_c__String__init(&msg->description)) {
    interface__msg__RadarWarn__fini(msg);
    return false;
  }
  // detected_at
  if (!builtin_interfaces__msg__Time__init(&msg->detected_at)) {
    interface__msg__RadarWarn__fini(msg);
    return false;
  }
  return true;
}

void
interface__msg__RadarWarn__fini(interface__msg__RadarWarn * msg)
{
  if (!msg) {
    return;
  }
  // header
  std_msgs__msg__Header__fini(&msg->header);
  // drone_id
  // x
  // y
  // z
  // confidence
  // warn_level
  rosidl_runtime_c__String__fini(&msg->warn_level);
  // description
  rosidl_runtime_c__String__fini(&msg->description);
  // detected_at
  builtin_interfaces__msg__Time__fini(&msg->detected_at);
}

bool
interface__msg__RadarWarn__are_equal(const interface__msg__RadarWarn * lhs, const interface__msg__RadarWarn * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // header
  if (!std_msgs__msg__Header__are_equal(
      &(lhs->header), &(rhs->header)))
  {
    return false;
  }
  // drone_id
  if (lhs->drone_id != rhs->drone_id) {
    return false;
  }
  // x
  if (lhs->x != rhs->x) {
    return false;
  }
  // y
  if (lhs->y != rhs->y) {
    return false;
  }
  // z
  if (lhs->z != rhs->z) {
    return false;
  }
  // confidence
  if (lhs->confidence != rhs->confidence) {
    return false;
  }
  // warn_level
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->warn_level), &(rhs->warn_level)))
  {
    return false;
  }
  // description
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->description), &(rhs->description)))
  {
    return false;
  }
  // detected_at
  if (!builtin_interfaces__msg__Time__are_equal(
      &(lhs->detected_at), &(rhs->detected_at)))
  {
    return false;
  }
  return true;
}

bool
interface__msg__RadarWarn__copy(
  const interface__msg__RadarWarn * input,
  interface__msg__RadarWarn * output)
{
  if (!input || !output) {
    return false;
  }
  // header
  if (!std_msgs__msg__Header__copy(
      &(input->header), &(output->header)))
  {
    return false;
  }
  // drone_id
  output->drone_id = input->drone_id;
  // x
  output->x = input->x;
  // y
  output->y = input->y;
  // z
  output->z = input->z;
  // confidence
  output->confidence = input->confidence;
  // warn_level
  if (!rosidl_runtime_c__String__copy(
      &(input->warn_level), &(output->warn_level)))
  {
    return false;
  }
  // description
  if (!rosidl_runtime_c__String__copy(
      &(input->description), &(output->description)))
  {
    return false;
  }
  // detected_at
  if (!builtin_interfaces__msg__Time__copy(
      &(input->detected_at), &(output->detected_at)))
  {
    return false;
  }
  return true;
}

interface__msg__RadarWarn *
interface__msg__RadarWarn__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  interface__msg__RadarWarn * msg = (interface__msg__RadarWarn *)allocator.allocate(sizeof(interface__msg__RadarWarn), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(interface__msg__RadarWarn));
  bool success = interface__msg__RadarWarn__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
interface__msg__RadarWarn__destroy(interface__msg__RadarWarn * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    interface__msg__RadarWarn__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
interface__msg__RadarWarn__Sequence__init(interface__msg__RadarWarn__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  interface__msg__RadarWarn * data = NULL;

  if (size) {
    data = (interface__msg__RadarWarn *)allocator.zero_allocate(size, sizeof(interface__msg__RadarWarn), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = interface__msg__RadarWarn__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        interface__msg__RadarWarn__fini(&data[i - 1]);
      }
      allocator.deallocate(data, allocator.state);
      return false;
    }
  }
  array->data = data;
  array->size = size;
  array->capacity = size;
  return true;
}

void
interface__msg__RadarWarn__Sequence__fini(interface__msg__RadarWarn__Sequence * array)
{
  if (!array) {
    return;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();

  if (array->data) {
    // ensure that data and capacity values are consistent
    assert(array->capacity > 0);
    // finalize all array elements
    for (size_t i = 0; i < array->capacity; ++i) {
      interface__msg__RadarWarn__fini(&array->data[i]);
    }
    allocator.deallocate(array->data, allocator.state);
    array->data = NULL;
    array->size = 0;
    array->capacity = 0;
  } else {
    // ensure that data, size, and capacity values are consistent
    assert(0 == array->size);
    assert(0 == array->capacity);
  }
}

interface__msg__RadarWarn__Sequence *
interface__msg__RadarWarn__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  interface__msg__RadarWarn__Sequence * array = (interface__msg__RadarWarn__Sequence *)allocator.allocate(sizeof(interface__msg__RadarWarn__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = interface__msg__RadarWarn__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
interface__msg__RadarWarn__Sequence__destroy(interface__msg__RadarWarn__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    interface__msg__RadarWarn__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
interface__msg__RadarWarn__Sequence__are_equal(const interface__msg__RadarWarn__Sequence * lhs, const interface__msg__RadarWarn__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!interface__msg__RadarWarn__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
interface__msg__RadarWarn__Sequence__copy(
  const interface__msg__RadarWarn__Sequence * input,
  interface__msg__RadarWarn__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(interface__msg__RadarWarn);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    interface__msg__RadarWarn * data =
      (interface__msg__RadarWarn *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!interface__msg__RadarWarn__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          interface__msg__RadarWarn__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!interface__msg__RadarWarn__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
