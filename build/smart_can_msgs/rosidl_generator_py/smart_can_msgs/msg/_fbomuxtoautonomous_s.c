// generated from rosidl_generator_py/resource/_idl_support.c.em
// with input from smart_can_msgs:msg/Fbomuxtoautonomous.idl
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
#include "smart_can_msgs/msg/detail/fbomuxtoautonomous__struct.h"
#include "smart_can_msgs/msg/detail/fbomuxtoautonomous__functions.h"


ROSIDL_GENERATOR_C_EXPORT
bool smart_can_msgs__msg__fbomuxtoautonomous__convert_from_py(PyObject * _pymsg, void * _ros_message)
{
  // check that the passed message is of the expected Python class
  {
    char full_classname_dest[58];
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
    assert(strncmp("smart_can_msgs.msg._fbomuxtoautonomous.Fbomuxtoautonomous", full_classname_dest, 57) == 0);
  }
  smart_can_msgs__msg__Fbomuxtoautonomous * ros_message = _ros_message;
  {  // fb_emergency
    PyObject * field = PyObject_GetAttrString(_pymsg, "fb_emergency");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->fb_emergency = (uint8_t)PyLong_AsUnsignedLong(field);
    Py_DECREF(field);
  }
  {  // fb_reverselight
    PyObject * field = PyObject_GetAttrString(_pymsg, "fb_reverselight");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->fb_reverselight = (uint8_t)PyLong_AsUnsignedLong(field);
    Py_DECREF(field);
  }
  {  // fb_rightsignal
    PyObject * field = PyObject_GetAttrString(_pymsg, "fb_rightsignal");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->fb_rightsignal = (uint8_t)PyLong_AsUnsignedLong(field);
    Py_DECREF(field);
  }
  {  // fb_windowresistance
    PyObject * field = PyObject_GetAttrString(_pymsg, "fb_windowresistance");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->fb_windowresistance = (uint8_t)PyLong_AsUnsignedLong(field);
    Py_DECREF(field);
  }
  {  // fb_leftsignal
    PyObject * field = PyObject_GetAttrString(_pymsg, "fb_leftsignal");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->fb_leftsignal = (uint8_t)PyLong_AsUnsignedLong(field);
    Py_DECREF(field);
  }
  {  // fb_interiorlight
    PyObject * field = PyObject_GetAttrString(_pymsg, "fb_interiorlight");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->fb_interiorlight = (uint8_t)PyLong_AsUnsignedLong(field);
    Py_DECREF(field);
  }
  {  // fb_drl
    PyObject * field = PyObject_GetAttrString(_pymsg, "fb_drl");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->fb_drl = (uint8_t)PyLong_AsUnsignedLong(field);
    Py_DECREF(field);
  }
  {  // fb_doorkeystatus
    PyObject * field = PyObject_GetAttrString(_pymsg, "fb_doorkeystatus");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->fb_doorkeystatus = (uint8_t)PyLong_AsUnsignedLong(field);
    Py_DECREF(field);
  }
  {  // fb_brakelight
    PyObject * field = PyObject_GetAttrString(_pymsg, "fb_brakelight");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->fb_brakelight = (uint8_t)PyLong_AsUnsignedLong(field);
    Py_DECREF(field);
  }
  {  // fb_batteryvoltage
    PyObject * field = PyObject_GetAttrString(_pymsg, "fb_batteryvoltage");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->fb_batteryvoltage = (uint8_t)PyLong_AsUnsignedLong(field);
    Py_DECREF(field);
  }
  {  // fb_chargeinput
    PyObject * field = PyObject_GetAttrString(_pymsg, "fb_chargeinput");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->fb_chargeinput = (uint8_t)PyLong_AsUnsignedLong(field);
    Py_DECREF(field);
  }
  {  // fb_highbeam
    PyObject * field = PyObject_GetAttrString(_pymsg, "fb_highbeam");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->fb_highbeam = (uint8_t)PyLong_AsUnsignedLong(field);
    Py_DECREF(field);
  }
  {  // fb_lowbeam
    PyObject * field = PyObject_GetAttrString(_pymsg, "fb_lowbeam");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->fb_lowbeam = (uint8_t)PyLong_AsUnsignedLong(field);
    Py_DECREF(field);
  }
  {  // fb_ignition
    PyObject * field = PyObject_GetAttrString(_pymsg, "fb_ignition");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->fb_ignition = (uint8_t)PyLong_AsUnsignedLong(field);
    Py_DECREF(field);
  }
  {  // fb_hazardouslight
    PyObject * field = PyObject_GetAttrString(_pymsg, "fb_hazardouslight");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->fb_hazardouslight = (uint8_t)PyLong_AsUnsignedLong(field);
    Py_DECREF(field);
  }
  {  // fb_vehiclestatus
    PyObject * field = PyObject_GetAttrString(_pymsg, "fb_vehiclestatus");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->fb_vehiclestatus = (uint8_t)PyLong_AsUnsignedLong(field);
    Py_DECREF(field);
  }
  {  // fb_leftdoorstatus
    PyObject * field = PyObject_GetAttrString(_pymsg, "fb_leftdoorstatus");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->fb_leftdoorstatus = (uint8_t)PyLong_AsUnsignedLong(field);
    Py_DECREF(field);
  }
  {  // fb_rightdoorstatus
    PyObject * field = PyObject_GetAttrString(_pymsg, "fb_rightdoorstatus");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->fb_rightdoorstatus = (uint8_t)PyLong_AsUnsignedLong(field);
    Py_DECREF(field);
  }
  {  // fb_batterysoc
    PyObject * field = PyObject_GetAttrString(_pymsg, "fb_batterysoc");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->fb_batterysoc = (uint8_t)PyLong_AsUnsignedLong(field);
    Py_DECREF(field);
  }
  {  // fb_errorpowertrain
    PyObject * field = PyObject_GetAttrString(_pymsg, "fb_errorpowertrain");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->fb_errorpowertrain = (uint8_t)PyLong_AsUnsignedLong(field);
    Py_DECREF(field);
  }
  {  // fb_errorbattery
    PyObject * field = PyObject_GetAttrString(_pymsg, "fb_errorbattery");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->fb_errorbattery = (uint8_t)PyLong_AsUnsignedLong(field);
    Py_DECREF(field);
  }
  {  // fb_brakepedal_voltage_en
    PyObject * field = PyObject_GetAttrString(_pymsg, "fb_brakepedal_voltage_en");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->fb_brakepedal_voltage_en = (uint8_t)PyLong_AsUnsignedLong(field);
    Py_DECREF(field);
  }

  return true;
}

ROSIDL_GENERATOR_C_EXPORT
PyObject * smart_can_msgs__msg__fbomuxtoautonomous__convert_to_py(void * raw_ros_message)
{
  /* NOTE(esteve): Call constructor of Fbomuxtoautonomous */
  PyObject * _pymessage = NULL;
  {
    PyObject * pymessage_module = PyImport_ImportModule("smart_can_msgs.msg._fbomuxtoautonomous");
    assert(pymessage_module);
    PyObject * pymessage_class = PyObject_GetAttrString(pymessage_module, "Fbomuxtoautonomous");
    assert(pymessage_class);
    Py_DECREF(pymessage_module);
    _pymessage = PyObject_CallObject(pymessage_class, NULL);
    Py_DECREF(pymessage_class);
    if (!_pymessage) {
      return NULL;
    }
  }
  smart_can_msgs__msg__Fbomuxtoautonomous * ros_message = (smart_can_msgs__msg__Fbomuxtoautonomous *)raw_ros_message;
  {  // fb_emergency
    PyObject * field = NULL;
    field = PyLong_FromUnsignedLong(ros_message->fb_emergency);
    {
      int rc = PyObject_SetAttrString(_pymessage, "fb_emergency", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // fb_reverselight
    PyObject * field = NULL;
    field = PyLong_FromUnsignedLong(ros_message->fb_reverselight);
    {
      int rc = PyObject_SetAttrString(_pymessage, "fb_reverselight", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // fb_rightsignal
    PyObject * field = NULL;
    field = PyLong_FromUnsignedLong(ros_message->fb_rightsignal);
    {
      int rc = PyObject_SetAttrString(_pymessage, "fb_rightsignal", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // fb_windowresistance
    PyObject * field = NULL;
    field = PyLong_FromUnsignedLong(ros_message->fb_windowresistance);
    {
      int rc = PyObject_SetAttrString(_pymessage, "fb_windowresistance", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // fb_leftsignal
    PyObject * field = NULL;
    field = PyLong_FromUnsignedLong(ros_message->fb_leftsignal);
    {
      int rc = PyObject_SetAttrString(_pymessage, "fb_leftsignal", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // fb_interiorlight
    PyObject * field = NULL;
    field = PyLong_FromUnsignedLong(ros_message->fb_interiorlight);
    {
      int rc = PyObject_SetAttrString(_pymessage, "fb_interiorlight", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // fb_drl
    PyObject * field = NULL;
    field = PyLong_FromUnsignedLong(ros_message->fb_drl);
    {
      int rc = PyObject_SetAttrString(_pymessage, "fb_drl", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // fb_doorkeystatus
    PyObject * field = NULL;
    field = PyLong_FromUnsignedLong(ros_message->fb_doorkeystatus);
    {
      int rc = PyObject_SetAttrString(_pymessage, "fb_doorkeystatus", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // fb_brakelight
    PyObject * field = NULL;
    field = PyLong_FromUnsignedLong(ros_message->fb_brakelight);
    {
      int rc = PyObject_SetAttrString(_pymessage, "fb_brakelight", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // fb_batteryvoltage
    PyObject * field = NULL;
    field = PyLong_FromUnsignedLong(ros_message->fb_batteryvoltage);
    {
      int rc = PyObject_SetAttrString(_pymessage, "fb_batteryvoltage", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // fb_chargeinput
    PyObject * field = NULL;
    field = PyLong_FromUnsignedLong(ros_message->fb_chargeinput);
    {
      int rc = PyObject_SetAttrString(_pymessage, "fb_chargeinput", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // fb_highbeam
    PyObject * field = NULL;
    field = PyLong_FromUnsignedLong(ros_message->fb_highbeam);
    {
      int rc = PyObject_SetAttrString(_pymessage, "fb_highbeam", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // fb_lowbeam
    PyObject * field = NULL;
    field = PyLong_FromUnsignedLong(ros_message->fb_lowbeam);
    {
      int rc = PyObject_SetAttrString(_pymessage, "fb_lowbeam", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // fb_ignition
    PyObject * field = NULL;
    field = PyLong_FromUnsignedLong(ros_message->fb_ignition);
    {
      int rc = PyObject_SetAttrString(_pymessage, "fb_ignition", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // fb_hazardouslight
    PyObject * field = NULL;
    field = PyLong_FromUnsignedLong(ros_message->fb_hazardouslight);
    {
      int rc = PyObject_SetAttrString(_pymessage, "fb_hazardouslight", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // fb_vehiclestatus
    PyObject * field = NULL;
    field = PyLong_FromUnsignedLong(ros_message->fb_vehiclestatus);
    {
      int rc = PyObject_SetAttrString(_pymessage, "fb_vehiclestatus", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // fb_leftdoorstatus
    PyObject * field = NULL;
    field = PyLong_FromUnsignedLong(ros_message->fb_leftdoorstatus);
    {
      int rc = PyObject_SetAttrString(_pymessage, "fb_leftdoorstatus", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // fb_rightdoorstatus
    PyObject * field = NULL;
    field = PyLong_FromUnsignedLong(ros_message->fb_rightdoorstatus);
    {
      int rc = PyObject_SetAttrString(_pymessage, "fb_rightdoorstatus", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // fb_batterysoc
    PyObject * field = NULL;
    field = PyLong_FromUnsignedLong(ros_message->fb_batterysoc);
    {
      int rc = PyObject_SetAttrString(_pymessage, "fb_batterysoc", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // fb_errorpowertrain
    PyObject * field = NULL;
    field = PyLong_FromUnsignedLong(ros_message->fb_errorpowertrain);
    {
      int rc = PyObject_SetAttrString(_pymessage, "fb_errorpowertrain", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // fb_errorbattery
    PyObject * field = NULL;
    field = PyLong_FromUnsignedLong(ros_message->fb_errorbattery);
    {
      int rc = PyObject_SetAttrString(_pymessage, "fb_errorbattery", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // fb_brakepedal_voltage_en
    PyObject * field = NULL;
    field = PyLong_FromUnsignedLong(ros_message->fb_brakepedal_voltage_en);
    {
      int rc = PyObject_SetAttrString(_pymessage, "fb_brakepedal_voltage_en", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }

  // ownership of _pymessage is transferred to the caller
  return _pymessage;
}
