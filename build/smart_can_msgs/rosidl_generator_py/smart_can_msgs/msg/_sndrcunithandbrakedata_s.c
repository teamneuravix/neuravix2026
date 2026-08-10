// generated from rosidl_generator_py/resource/_idl_support.c.em
// with input from smart_can_msgs:msg/Sndrcunithandbrakedata.idl
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
#include "smart_can_msgs/msg/detail/sndrcunithandbrakedata__struct.h"
#include "smart_can_msgs/msg/detail/sndrcunithandbrakedata__functions.h"


ROSIDL_GENERATOR_C_EXPORT
bool smart_can_msgs__msg__sndrcunithandbrakedata__convert_from_py(PyObject * _pymsg, void * _ros_message)
{
  // check that the passed message is of the expected Python class
  {
    char full_classname_dest[66];
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
    assert(strncmp("smart_can_msgs.msg._sndrcunithandbrakedata.Sndrcunithandbrakedata", full_classname_dest, 65) == 0);
  }
  smart_can_msgs__msg__Sndrcunithandbrakedata * ros_message = _ros_message;
  {  // rc_hb_pwmvalue
    PyObject * field = PyObject_GetAttrString(_pymsg, "rc_hb_pwmvalue");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->rc_hb_pwmvalue = (uint16_t)PyLong_AsUnsignedLong(field);
    Py_DECREF(field);
  }
  {  // rc_handbrake_press
    PyObject * field = PyObject_GetAttrString(_pymsg, "rc_handbrake_press");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->rc_handbrake_press = (uint8_t)PyLong_AsUnsignedLong(field);
    Py_DECREF(field);
  }
  {  // rc_handbrake_free
    PyObject * field = PyObject_GetAttrString(_pymsg, "rc_handbrake_free");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->rc_handbrake_free = (uint8_t)PyLong_AsUnsignedLong(field);
    Py_DECREF(field);
  }
  {  // rc_handbrakedata
    PyObject * field = PyObject_GetAttrString(_pymsg, "rc_handbrakedata");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->rc_handbrakedata = (uint8_t)PyLong_AsUnsignedLong(field);
    Py_DECREF(field);
  }

  return true;
}

ROSIDL_GENERATOR_C_EXPORT
PyObject * smart_can_msgs__msg__sndrcunithandbrakedata__convert_to_py(void * raw_ros_message)
{
  /* NOTE(esteve): Call constructor of Sndrcunithandbrakedata */
  PyObject * _pymessage = NULL;
  {
    PyObject * pymessage_module = PyImport_ImportModule("smart_can_msgs.msg._sndrcunithandbrakedata");
    assert(pymessage_module);
    PyObject * pymessage_class = PyObject_GetAttrString(pymessage_module, "Sndrcunithandbrakedata");
    assert(pymessage_class);
    Py_DECREF(pymessage_module);
    _pymessage = PyObject_CallObject(pymessage_class, NULL);
    Py_DECREF(pymessage_class);
    if (!_pymessage) {
      return NULL;
    }
  }
  smart_can_msgs__msg__Sndrcunithandbrakedata * ros_message = (smart_can_msgs__msg__Sndrcunithandbrakedata *)raw_ros_message;
  {  // rc_hb_pwmvalue
    PyObject * field = NULL;
    field = PyLong_FromUnsignedLong(ros_message->rc_hb_pwmvalue);
    {
      int rc = PyObject_SetAttrString(_pymessage, "rc_hb_pwmvalue", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // rc_handbrake_press
    PyObject * field = NULL;
    field = PyLong_FromUnsignedLong(ros_message->rc_handbrake_press);
    {
      int rc = PyObject_SetAttrString(_pymessage, "rc_handbrake_press", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // rc_handbrake_free
    PyObject * field = NULL;
    field = PyLong_FromUnsignedLong(ros_message->rc_handbrake_free);
    {
      int rc = PyObject_SetAttrString(_pymessage, "rc_handbrake_free", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // rc_handbrakedata
    PyObject * field = NULL;
    field = PyLong_FromUnsignedLong(ros_message->rc_handbrakedata);
    {
      int rc = PyObject_SetAttrString(_pymessage, "rc_handbrakedata", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }

  // ownership of _pymessage is transferred to the caller
  return _pymessage;
}
