// generated from rosidl_generator_py/resource/_idl_support.c.em
// with input from smart_can_msgs:msg/Feedbacksteeringangle.idl
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
#include "smart_can_msgs/msg/detail/feedbacksteeringangle__struct.h"
#include "smart_can_msgs/msg/detail/feedbacksteeringangle__functions.h"


ROSIDL_GENERATOR_C_EXPORT
bool smart_can_msgs__msg__feedbacksteeringangle__convert_from_py(PyObject * _pymsg, void * _ros_message)
{
  // check that the passed message is of the expected Python class
  {
    char full_classname_dest[64];
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
    assert(strncmp("smart_can_msgs.msg._feedbacksteeringangle.Feedbacksteeringangle", full_classname_dest, 63) == 0);
  }
  smart_can_msgs__msg__Feedbacksteeringangle * ros_message = _ros_message;
  {  // feedbacksteeringangle
    PyObject * field = PyObject_GetAttrString(_pymsg, "feedbacksteeringangle");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->feedbacksteeringangle = (int8_t)PyLong_AsLong(field);
    Py_DECREF(field);
  }
  {  // feedbackbrakepedalangle
    PyObject * field = PyObject_GetAttrString(_pymsg, "feedbackbrakepedalangle");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->feedbackbrakepedalangle = (int8_t)PyLong_AsLong(field);
    Py_DECREF(field);
  }

  return true;
}

ROSIDL_GENERATOR_C_EXPORT
PyObject * smart_can_msgs__msg__feedbacksteeringangle__convert_to_py(void * raw_ros_message)
{
  /* NOTE(esteve): Call constructor of Feedbacksteeringangle */
  PyObject * _pymessage = NULL;
  {
    PyObject * pymessage_module = PyImport_ImportModule("smart_can_msgs.msg._feedbacksteeringangle");
    assert(pymessage_module);
    PyObject * pymessage_class = PyObject_GetAttrString(pymessage_module, "Feedbacksteeringangle");
    assert(pymessage_class);
    Py_DECREF(pymessage_module);
    _pymessage = PyObject_CallObject(pymessage_class, NULL);
    Py_DECREF(pymessage_class);
    if (!_pymessage) {
      return NULL;
    }
  }
  smart_can_msgs__msg__Feedbacksteeringangle * ros_message = (smart_can_msgs__msg__Feedbacksteeringangle *)raw_ros_message;
  {  // feedbacksteeringangle
    PyObject * field = NULL;
    field = PyLong_FromLong(ros_message->feedbacksteeringangle);
    {
      int rc = PyObject_SetAttrString(_pymessage, "feedbacksteeringangle", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // feedbackbrakepedalangle
    PyObject * field = NULL;
    field = PyLong_FromLong(ros_message->feedbackbrakepedalangle);
    {
      int rc = PyObject_SetAttrString(_pymessage, "feedbackbrakepedalangle", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }

  // ownership of _pymessage is transferred to the caller
  return _pymessage;
}
