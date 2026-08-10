// generated from rosidl_generator_py/resource/_idl_support.c.em
// with input from smart_can_msgs:msg/Rcunittoomux.idl
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
#include "smart_can_msgs/msg/detail/rcunittoomux__struct.h"
#include "smart_can_msgs/msg/detail/rcunittoomux__functions.h"


ROSIDL_GENERATOR_C_EXPORT
bool smart_can_msgs__msg__rcunittoomux__convert_from_py(PyObject * _pymsg, void * _ros_message)
{
  // check that the passed message is of the expected Python class
  {
    char full_classname_dest[46];
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
    assert(strncmp("smart_can_msgs.msg._rcunittoomux.Rcunittoomux", full_classname_dest, 45) == 0);
  }
  smart_can_msgs__msg__Rcunittoomux * ros_message = _ros_message;
  {  // autonomous_emergency
    PyObject * field = PyObject_GetAttrString(_pymsg, "autonomous_emergency");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->autonomous_emergency = (int8_t)PyLong_AsLong(field);
    Py_DECREF(field);
  }
  {  // rc_windowresintance
    PyObject * field = PyObject_GetAttrString(_pymsg, "rc_windowresintance");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->rc_windowresintance = (uint8_t)PyLong_AsUnsignedLong(field);
    Py_DECREF(field);
  }
  {  // rc_interiorlight
    PyObject * field = PyObject_GetAttrString(_pymsg, "rc_interiorlight");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->rc_interiorlight = (uint8_t)PyLong_AsUnsignedLong(field);
    Py_DECREF(field);
  }
  {  // rc_reverselight
    PyObject * field = PyObject_GetAttrString(_pymsg, "rc_reverselight");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->rc_reverselight = (uint8_t)PyLong_AsUnsignedLong(field);
    Py_DECREF(field);
  }
  {  // rc_drl
    PyObject * field = PyObject_GetAttrString(_pymsg, "rc_drl");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->rc_drl = (uint8_t)PyLong_AsUnsignedLong(field);
    Py_DECREF(field);
  }
  {  // rc_brakelight
    PyObject * field = PyObject_GetAttrString(_pymsg, "rc_brakelight");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->rc_brakelight = (uint8_t)PyLong_AsUnsignedLong(field);
    Py_DECREF(field);
  }
  {  // autonomous_door_open
    PyObject * field = PyObject_GetAttrString(_pymsg, "autonomous_door_open");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->autonomous_door_open = (int8_t)PyLong_AsLong(field);
    Py_DECREF(field);
  }
  {  // autonomous_door_close
    PyObject * field = PyObject_GetAttrString(_pymsg, "autonomous_door_close");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->autonomous_door_close = (int8_t)PyLong_AsLong(field);
    Py_DECREF(field);
  }
  {  // rc_signalstatus
    PyObject * field = PyObject_GetAttrString(_pymsg, "rc_signalstatus");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->rc_signalstatus = (uint8_t)PyLong_AsUnsignedLong(field);
    Py_DECREF(field);
  }
  {  // rc_lowbeam
    PyObject * field = PyObject_GetAttrString(_pymsg, "rc_lowbeam");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->rc_lowbeam = (uint8_t)PyLong_AsUnsignedLong(field);
    Py_DECREF(field);
  }
  {  // rc_highbeam
    PyObject * field = PyObject_GetAttrString(_pymsg, "rc_highbeam");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->rc_highbeam = (uint8_t)PyLong_AsUnsignedLong(field);
    Py_DECREF(field);
  }
  {  // rc_selectiongear
    PyObject * field = PyObject_GetAttrString(_pymsg, "rc_selectiongear");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->rc_selectiongear = (uint8_t)PyLong_AsUnsignedLong(field);
    Py_DECREF(field);
  }
  {  // rc_ignition
    PyObject * field = PyObject_GetAttrString(_pymsg, "rc_ignition");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->rc_ignition = (uint8_t)PyLong_AsUnsignedLong(field);
    Py_DECREF(field);
  }

  return true;
}

ROSIDL_GENERATOR_C_EXPORT
PyObject * smart_can_msgs__msg__rcunittoomux__convert_to_py(void * raw_ros_message)
{
  /* NOTE(esteve): Call constructor of Rcunittoomux */
  PyObject * _pymessage = NULL;
  {
    PyObject * pymessage_module = PyImport_ImportModule("smart_can_msgs.msg._rcunittoomux");
    assert(pymessage_module);
    PyObject * pymessage_class = PyObject_GetAttrString(pymessage_module, "Rcunittoomux");
    assert(pymessage_class);
    Py_DECREF(pymessage_module);
    _pymessage = PyObject_CallObject(pymessage_class, NULL);
    Py_DECREF(pymessage_class);
    if (!_pymessage) {
      return NULL;
    }
  }
  smart_can_msgs__msg__Rcunittoomux * ros_message = (smart_can_msgs__msg__Rcunittoomux *)raw_ros_message;
  {  // autonomous_emergency
    PyObject * field = NULL;
    field = PyLong_FromLong(ros_message->autonomous_emergency);
    {
      int rc = PyObject_SetAttrString(_pymessage, "autonomous_emergency", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // rc_windowresintance
    PyObject * field = NULL;
    field = PyLong_FromUnsignedLong(ros_message->rc_windowresintance);
    {
      int rc = PyObject_SetAttrString(_pymessage, "rc_windowresintance", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // rc_interiorlight
    PyObject * field = NULL;
    field = PyLong_FromUnsignedLong(ros_message->rc_interiorlight);
    {
      int rc = PyObject_SetAttrString(_pymessage, "rc_interiorlight", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // rc_reverselight
    PyObject * field = NULL;
    field = PyLong_FromUnsignedLong(ros_message->rc_reverselight);
    {
      int rc = PyObject_SetAttrString(_pymessage, "rc_reverselight", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // rc_drl
    PyObject * field = NULL;
    field = PyLong_FromUnsignedLong(ros_message->rc_drl);
    {
      int rc = PyObject_SetAttrString(_pymessage, "rc_drl", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // rc_brakelight
    PyObject * field = NULL;
    field = PyLong_FromUnsignedLong(ros_message->rc_brakelight);
    {
      int rc = PyObject_SetAttrString(_pymessage, "rc_brakelight", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // autonomous_door_open
    PyObject * field = NULL;
    field = PyLong_FromLong(ros_message->autonomous_door_open);
    {
      int rc = PyObject_SetAttrString(_pymessage, "autonomous_door_open", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // autonomous_door_close
    PyObject * field = NULL;
    field = PyLong_FromLong(ros_message->autonomous_door_close);
    {
      int rc = PyObject_SetAttrString(_pymessage, "autonomous_door_close", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // rc_signalstatus
    PyObject * field = NULL;
    field = PyLong_FromUnsignedLong(ros_message->rc_signalstatus);
    {
      int rc = PyObject_SetAttrString(_pymessage, "rc_signalstatus", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // rc_lowbeam
    PyObject * field = NULL;
    field = PyLong_FromUnsignedLong(ros_message->rc_lowbeam);
    {
      int rc = PyObject_SetAttrString(_pymessage, "rc_lowbeam", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // rc_highbeam
    PyObject * field = NULL;
    field = PyLong_FromUnsignedLong(ros_message->rc_highbeam);
    {
      int rc = PyObject_SetAttrString(_pymessage, "rc_highbeam", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // rc_selectiongear
    PyObject * field = NULL;
    field = PyLong_FromUnsignedLong(ros_message->rc_selectiongear);
    {
      int rc = PyObject_SetAttrString(_pymessage, "rc_selectiongear", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // rc_ignition
    PyObject * field = NULL;
    field = PyLong_FromUnsignedLong(ros_message->rc_ignition);
    {
      int rc = PyObject_SetAttrString(_pymessage, "rc_ignition", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }

  // ownership of _pymessage is transferred to the caller
  return _pymessage;
}
