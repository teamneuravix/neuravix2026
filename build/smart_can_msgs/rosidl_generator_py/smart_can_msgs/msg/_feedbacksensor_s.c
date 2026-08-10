// generated from rosidl_generator_py/resource/_idl_support.c.em
// with input from smart_can_msgs:msg/Feedbacksensor.idl
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
#include "smart_can_msgs/msg/detail/feedbacksensor__struct.h"
#include "smart_can_msgs/msg/detail/feedbacksensor__functions.h"


ROSIDL_GENERATOR_C_EXPORT
bool smart_can_msgs__msg__feedbacksensor__convert_from_py(PyObject * _pymsg, void * _ros_message)
{
  // check that the passed message is of the expected Python class
  {
    char full_classname_dest[50];
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
    assert(strncmp("smart_can_msgs.msg._feedbacksensor.Feedbacksensor", full_classname_dest, 49) == 0);
  }
  smart_can_msgs__msg__Feedbacksensor * ros_message = _ros_message;
  {  // steeringanglesensorhamdata
    PyObject * field = PyObject_GetAttrString(_pymsg, "steeringanglesensorhamdata");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->steeringanglesensorhamdata = (uint8_t)PyLong_AsUnsignedLong(field);
    Py_DECREF(field);
  }
  {  // brakepedalsensorhamdata
    PyObject * field = PyObject_GetAttrString(_pymsg, "brakepedalsensorhamdata");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->brakepedalsensorhamdata = (uint8_t)PyLong_AsUnsignedLong(field);
    Py_DECREF(field);
  }
  {  // handbrakesensor
    PyObject * field = PyObject_GetAttrString(_pymsg, "handbrakesensor");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->handbrakesensor = (uint8_t)PyLong_AsUnsignedLong(field);
    Py_DECREF(field);
  }
  {  // handbrakesensor_hamdata
    PyObject * field = PyObject_GetAttrString(_pymsg, "handbrakesensor_hamdata");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->handbrakesensor_hamdata = (uint8_t)PyLong_AsUnsignedLong(field);
    Py_DECREF(field);
  }
  {  // indir
    PyObject * field = PyObject_GetAttrString(_pymsg, "indir");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->indir = (uint8_t)PyLong_AsUnsignedLong(field);
    Py_DECREF(field);
  }
  {  // kaldir
    PyObject * field = PyObject_GetAttrString(_pymsg, "kaldir");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->kaldir = (uint8_t)PyLong_AsUnsignedLong(field);
    Py_DECREF(field);
  }
  {  // butonindir
    PyObject * field = PyObject_GetAttrString(_pymsg, "butonindir");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->butonindir = (uint8_t)PyLong_AsUnsignedLong(field);
    Py_DECREF(field);
  }
  {  // butonkaldir
    PyObject * field = PyObject_GetAttrString(_pymsg, "butonkaldir");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->butonkaldir = (uint8_t)PyLong_AsUnsignedLong(field);
    Py_DECREF(field);
  }

  return true;
}

ROSIDL_GENERATOR_C_EXPORT
PyObject * smart_can_msgs__msg__feedbacksensor__convert_to_py(void * raw_ros_message)
{
  /* NOTE(esteve): Call constructor of Feedbacksensor */
  PyObject * _pymessage = NULL;
  {
    PyObject * pymessage_module = PyImport_ImportModule("smart_can_msgs.msg._feedbacksensor");
    assert(pymessage_module);
    PyObject * pymessage_class = PyObject_GetAttrString(pymessage_module, "Feedbacksensor");
    assert(pymessage_class);
    Py_DECREF(pymessage_module);
    _pymessage = PyObject_CallObject(pymessage_class, NULL);
    Py_DECREF(pymessage_class);
    if (!_pymessage) {
      return NULL;
    }
  }
  smart_can_msgs__msg__Feedbacksensor * ros_message = (smart_can_msgs__msg__Feedbacksensor *)raw_ros_message;
  {  // steeringanglesensorhamdata
    PyObject * field = NULL;
    field = PyLong_FromUnsignedLong(ros_message->steeringanglesensorhamdata);
    {
      int rc = PyObject_SetAttrString(_pymessage, "steeringanglesensorhamdata", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // brakepedalsensorhamdata
    PyObject * field = NULL;
    field = PyLong_FromUnsignedLong(ros_message->brakepedalsensorhamdata);
    {
      int rc = PyObject_SetAttrString(_pymessage, "brakepedalsensorhamdata", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // handbrakesensor
    PyObject * field = NULL;
    field = PyLong_FromUnsignedLong(ros_message->handbrakesensor);
    {
      int rc = PyObject_SetAttrString(_pymessage, "handbrakesensor", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // handbrakesensor_hamdata
    PyObject * field = NULL;
    field = PyLong_FromUnsignedLong(ros_message->handbrakesensor_hamdata);
    {
      int rc = PyObject_SetAttrString(_pymessage, "handbrakesensor_hamdata", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // indir
    PyObject * field = NULL;
    field = PyLong_FromUnsignedLong(ros_message->indir);
    {
      int rc = PyObject_SetAttrString(_pymessage, "indir", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // kaldir
    PyObject * field = NULL;
    field = PyLong_FromUnsignedLong(ros_message->kaldir);
    {
      int rc = PyObject_SetAttrString(_pymessage, "kaldir", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // butonindir
    PyObject * field = NULL;
    field = PyLong_FromUnsignedLong(ros_message->butonindir);
    {
      int rc = PyObject_SetAttrString(_pymessage, "butonindir", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // butonkaldir
    PyObject * field = NULL;
    field = PyLong_FromUnsignedLong(ros_message->butonkaldir);
    {
      int rc = PyObject_SetAttrString(_pymessage, "butonkaldir", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }

  // ownership of _pymessage is transferred to the caller
  return _pymessage;
}
