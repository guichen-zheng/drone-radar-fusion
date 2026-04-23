// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from interface:msg/DroneDetect.idl
// generated code does not contain a copyright notice
#include "interface/msg/detail/drone_detect__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


// Include directives for member types
// Member `header`
#include "std_msgs/msg/detail/header__functions.h"
// Member `label`
#include "rosidl_runtime_c/string_functions.h"

bool
interface__msg__DroneDetect__init(interface__msg__DroneDetect * msg)
{
  if (!msg) {
    return false;
  }
  // header
  if (!std_msgs__msg__Header__init(&msg->header)) {
    interface__msg__DroneDetect__fini(msg);
    return false;
  }
  // drone_id
  // x
  // y
  // z
  // vx
  // vy
  // vz
  // confidence
  // bbox_x
  // bbox_y
  // bbox_w
  // bbox_h
  // label
  if (!rosidl_runtime_c__String__init(&msg->label)) {
    interface__msg__DroneDetect__fini(msg);
    return false;
  }
  // is_tracked
  // lat
  // lng
  return true;
}

void
interface__msg__DroneDetect__fini(interface__msg__DroneDetect * msg)
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
  // vx
  // vy
  // vz
  // confidence
  // bbox_x
  // bbox_y
  // bbox_w
  // bbox_h
  // label
  rosidl_runtime_c__String__fini(&msg->label);
  // is_tracked
  // lat
  // lng
}

bool
interface__msg__DroneDetect__are_equal(const interface__msg__DroneDetect * lhs, const interface__msg__DroneDetect * rhs)
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
  // vx
  if (lhs->vx != rhs->vx) {
    return false;
  }
  // vy
  if (lhs->vy != rhs->vy) {
    return false;
  }
  // vz
  if (lhs->vz != rhs->vz) {
    return false;
  }
  // confidence
  if (lhs->confidence != rhs->confidence) {
    return false;
  }
  // bbox_x
  if (lhs->bbox_x != rhs->bbox_x) {
    return false;
  }
  // bbox_y
  if (lhs->bbox_y != rhs->bbox_y) {
    return false;
  }
  // bbox_w
  if (lhs->bbox_w != rhs->bbox_w) {
    return false;
  }
  // bbox_h
  if (lhs->bbox_h != rhs->bbox_h) {
    return false;
  }
  // label
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->label), &(rhs->label)))
  {
    return false;
  }
  // is_tracked
  if (lhs->is_tracked != rhs->is_tracked) {
    return false;
  }
  // lat
  if (lhs->lat != rhs->lat) {
    return false;
  }
  // lng
  if (lhs->lng != rhs->lng) {
    return false;
  }
  return true;
}

bool
interface__msg__DroneDetect__copy(
  const interface__msg__DroneDetect * input,
  interface__msg__DroneDetect * output)
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
  // vx
  output->vx = input->vx;
  // vy
  output->vy = input->vy;
  // vz
  output->vz = input->vz;
  // confidence
  output->confidence = input->confidence;
  // bbox_x
  output->bbox_x = input->bbox_x;
  // bbox_y
  output->bbox_y = input->bbox_y;
  // bbox_w
  output->bbox_w = input->bbox_w;
  // bbox_h
  output->bbox_h = input->bbox_h;
  // label
  if (!rosidl_runtime_c__String__copy(
      &(input->label), &(output->label)))
  {
    return false;
  }
  // is_tracked
  output->is_tracked = input->is_tracked;
  // lat
  output->lat = input->lat;
  // lng
  output->lng = input->lng;
  return true;
}

interface__msg__DroneDetect *
interface__msg__DroneDetect__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  interface__msg__DroneDetect * msg = (interface__msg__DroneDetect *)allocator.allocate(sizeof(interface__msg__DroneDetect), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(interface__msg__DroneDetect));
  bool success = interface__msg__DroneDetect__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
interface__msg__DroneDetect__destroy(interface__msg__DroneDetect * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    interface__msg__DroneDetect__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
interface__msg__DroneDetect__Sequence__init(interface__msg__DroneDetect__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  interface__msg__DroneDetect * data = NULL;

  if (size) {
    data = (interface__msg__DroneDetect *)allocator.zero_allocate(size, sizeof(interface__msg__DroneDetect), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = interface__msg__DroneDetect__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        interface__msg__DroneDetect__fini(&data[i - 1]);
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
interface__msg__DroneDetect__Sequence__fini(interface__msg__DroneDetect__Sequence * array)
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
      interface__msg__DroneDetect__fini(&array->data[i]);
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

interface__msg__DroneDetect__Sequence *
interface__msg__DroneDetect__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  interface__msg__DroneDetect__Sequence * array = (interface__msg__DroneDetect__Sequence *)allocator.allocate(sizeof(interface__msg__DroneDetect__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = interface__msg__DroneDetect__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
interface__msg__DroneDetect__Sequence__destroy(interface__msg__DroneDetect__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    interface__msg__DroneDetect__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
interface__msg__DroneDetect__Sequence__are_equal(const interface__msg__DroneDetect__Sequence * lhs, const interface__msg__DroneDetect__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!interface__msg__DroneDetect__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
interface__msg__DroneDetect__Sequence__copy(
  const interface__msg__DroneDetect__Sequence * input,
  interface__msg__DroneDetect__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(interface__msg__DroneDetect);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    interface__msg__DroneDetect * data =
      (interface__msg__DroneDetect *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!interface__msg__DroneDetect__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          interface__msg__DroneDetect__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!interface__msg__DroneDetect__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
