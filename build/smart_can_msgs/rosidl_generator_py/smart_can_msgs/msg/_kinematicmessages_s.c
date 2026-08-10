// generated from rosidl_generator_py/resource/_idl_support.c.em
// with input from smart_can_msgs:msg/Kinematicmessages.idl
// generated code does not contain a copyright notice
#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION
#include <Python.h>
#include <stdbool.h>
#ifndef _WIN32
# pragma GCC diagnostic push
# pragma GCC diagnostic ignored "-Wunused-function"
#endif
#include "numpy/ndarrayobject.h"
#ifndef _WIN32
# pragma GCC diagnostic pop
#endif
#include "rosidl_runtime_c/visibility_control.h"
#include "smart_can_msgs/msg/detail/kinematicmessages__struct.h"
#include "smart_can_msgs/msg/detail/kinematicmessages__functions.h"


ROSIDL_GENERATOR_C_EXPORT
bool smart_can_msgs__msg__kinematicmessages__convert_from_py(PyObject * _pymsg, void * _ros_message)
{
  // check that the passed message is of the expected Python class
  {
    char full_classname_dest[56];
    {
      char * class_name = NULL;
      char * module_name = NULL;
      {
        PyObject * class_attr = PyObject_GetAttrString(_pymsg, "__class__");
        if (class_attr) {
          PyObject * name_attr = PyObject_GetAttrString(class_attr, "__name__");
          if (name_attr) {
            class_name = (char *)PyUnicode_1BYTE_DATA(name_attr);
            Py_DECREF(name_attr);
          }
          PyObject * module_attr = PyObject_GetAttrString(class_attr, "__module__");
          if (module_attr) {
            module_name = (char *)PyUnicode_1BYTE_DATA(module_attr);
            Py_DECREF(module_attr);
          }
          Py_DECREF(class_attr);
        }
      }
      if (!class_name || !module_name) {
        return false;
      }
      snprintf(full_classname_dest, sizeof(full_classname_dest), "%s.%s", module_name, class_name);
    }
    assert(strncmp("smart_can_msgs.msg._kinematicmessages.Kinematicmessages", full_classname_dest, 55) == 0);
  }
  smart_can_msgs__msg__Kinematicmessages * ros_message = _ros_message;
  {  // joint_type
    PyObject * field = PyObject_GetAttrString(_pymsg, "joint_type");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->joint_type = (uint8_t)PyLong_AsUnsignedLong(field);
    Py_DECREF(field);
  }
  {  // angle
    PyObject * field = PyObject_GetAttrString(_pymsg, "angle");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->angle = (float)PyFloat_AS_DOUBLE(field);
    Py_DECREF(field);
  }
  {  // angle_y
    PyObject * field = PyObject_GetAttrString(_pymsg, "angle_y");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->angle_y = (float)PyFloat_AS_DOUBLE(field);
    Py_DECREF(field);
  }
  {  // angular_velocity
    PyObject * field = PyObject_GetAttrString(_pymsg, "angular_velocity");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->angular_velocity = (float)PyFloat_AS_DOUBLE(field);
    Py_DECREF(field);
  }
  {  // link_length
    PyObject * field = PyObject_GetAttrString(_pymsg, "link_length");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->link_length = (float)PyFloat_AS_DOUBLE(field);
    Py_DECREF(field);
  }

  return true;
}

ROSIDL_GENERATOR_C_EXPORT
PyObject * smart_can_msgs__msg__kinematicmessages__convert_to_py(void * raw_ros_message)
{
  /* NOTE(esteve): Call constructor of Kinematicmessages */
  PyObject * _pymessage = NULL;
  {
    PyObject * pymessage_module = PyImport_ImportModule("smart_can_msgs.msg._kinematicmessages");
    assert(pymessage_module);
    PyObject * pymessage_class = PyObject_GetAttrString(pymessage_module, "Kinematicmessages");
    assert(pymessage_class);
    Py_DECREF(pymessage_module);
    _pymessage = PyObject_CallObject(pymessage_class, NULL);
    Py_DECREF(pymessage_class);
    if (!_pymessage) {
      return NULL;
    }
  }
  smart_can_msgs__msg__Kinematicmessages * ros_message = (smart_can_msgs__msg__Kinematicmessages *)raw_ros_message;
  {  // joint_type
    PyObject * field = NULL;
    field = PyLong_FromUnsignedLong(ros_message->joint_type);
    {
      int rc = PyObject_SetAttrString(_pymessage, "joint_type", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // angle
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->angle);
    {
      int rc = PyObject_SetAttrString(_pymessage, "angle", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // angle_y
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->angle_y);
    {
      int rc = PyObject_SetAttrString(_pymessage, "angle_y", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // angular_velocity
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->angular_velocity);
    {
      int rc = PyObject_SetAttrString(_pymessage, "angular_velocity", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // link_length
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->link_length);
    {
      int rc = PyObject_SetAttrString(_pymessage, "link_length", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }

  // ownership of _pymessage is transferred to the caller
  return _pymessage;
}
