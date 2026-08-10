# generated from rosidl_generator_py/resource/_idl.py.em
# with input from smart_can_msgs:msg/Fbomuxtoautonomous.idl
# generated code does not contain a copyright notice


# Import statements for member types

import builtins  # noqa: E402, I100

import rosidl_parser.definition  # noqa: E402, I100


class Metaclass_Fbomuxtoautonomous(type):
    """Metaclass of message 'Fbomuxtoautonomous'."""

    _CREATE_ROS_MESSAGE = None
    _CONVERT_FROM_PY = None
    _CONVERT_TO_PY = None
    _DESTROY_ROS_MESSAGE = None
    _TYPE_SUPPORT = None

    __constants = {
    }

    @classmethod
    def __import_type_support__(cls):
        try:
            from rosidl_generator_py import import_type_support
            module = import_type_support('smart_can_msgs')
        except ImportError:
            import logging
            import traceback
            logger = logging.getLogger(
                'smart_can_msgs.msg.Fbomuxtoautonomous')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__msg__fbomuxtoautonomous
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__msg__fbomuxtoautonomous
            cls._CONVERT_TO_PY = module.convert_to_py_msg__msg__fbomuxtoautonomous
            cls._TYPE_SUPPORT = module.type_support_msg__msg__fbomuxtoautonomous
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__msg__fbomuxtoautonomous

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
        }


class Fbomuxtoautonomous(metaclass=Metaclass_Fbomuxtoautonomous):
    """Message class 'Fbomuxtoautonomous'."""

    __slots__ = [
        '_fb_emergency',
        '_fb_reverselight',
        '_fb_rightsignal',
        '_fb_windowresistance',
        '_fb_leftsignal',
        '_fb_interiorlight',
        '_fb_drl',
        '_fb_doorkeystatus',
        '_fb_brakelight',
        '_fb_batteryvoltage',
        '_fb_chargeinput',
        '_fb_highbeam',
        '_fb_lowbeam',
        '_fb_ignition',
        '_fb_hazardouslight',
        '_fb_vehiclestatus',
        '_fb_leftdoorstatus',
        '_fb_rightdoorstatus',
        '_fb_batterysoc',
        '_fb_errorpowertrain',
        '_fb_errorbattery',
        '_fb_brakepedal_voltage_en',
    ]

    _fields_and_field_types = {
        'fb_emergency': 'uint8',
        'fb_reverselight': 'uint8',
        'fb_rightsignal': 'uint8',
        'fb_windowresistance': 'uint8',
        'fb_leftsignal': 'uint8',
        'fb_interiorlight': 'uint8',
        'fb_drl': 'uint8',
        'fb_doorkeystatus': 'uint8',
        'fb_brakelight': 'uint8',
        'fb_batteryvoltage': 'uint8',
        'fb_chargeinput': 'uint8',
        'fb_highbeam': 'uint8',
        'fb_lowbeam': 'uint8',
        'fb_ignition': 'uint8',
        'fb_hazardouslight': 'uint8',
        'fb_vehiclestatus': 'uint8',
        'fb_leftdoorstatus': 'uint8',
        'fb_rightdoorstatus': 'uint8',
        'fb_batterysoc': 'uint8',
        'fb_errorpowertrain': 'uint8',
        'fb_errorbattery': 'uint8',
        'fb_brakepedal_voltage_en': 'uint8',
    }

    SLOT_TYPES = (
        rosidl_parser.definition.BasicType('uint8'),  # noqa: E501
        rosidl_parser.definition.BasicType('uint8'),  # noqa: E501
        rosidl_parser.definition.BasicType('uint8'),  # noqa: E501
        rosidl_parser.definition.BasicType('uint8'),  # noqa: E501
        rosidl_parser.definition.BasicType('uint8'),  # noqa: E501
        rosidl_parser.definition.BasicType('uint8'),  # noqa: E501
        rosidl_parser.definition.BasicType('uint8'),  # noqa: E501
        rosidl_parser.definition.BasicType('uint8'),  # noqa: E501
        rosidl_parser.definition.BasicType('uint8'),  # noqa: E501
        rosidl_parser.definition.BasicType('uint8'),  # noqa: E501
        rosidl_parser.definition.BasicType('uint8'),  # noqa: E501
        rosidl_parser.definition.BasicType('uint8'),  # noqa: E501
        rosidl_parser.definition.BasicType('uint8'),  # noqa: E501
        rosidl_parser.definition.BasicType('uint8'),  # noqa: E501
        rosidl_parser.definition.BasicType('uint8'),  # noqa: E501
        rosidl_parser.definition.BasicType('uint8'),  # noqa: E501
        rosidl_parser.definition.BasicType('uint8'),  # noqa: E501
        rosidl_parser.definition.BasicType('uint8'),  # noqa: E501
        rosidl_parser.definition.BasicType('uint8'),  # noqa: E501
        rosidl_parser.definition.BasicType('uint8'),  # noqa: E501
        rosidl_parser.definition.BasicType('uint8'),  # noqa: E501
        rosidl_parser.definition.BasicType('uint8'),  # noqa: E501
    )

    def __init__(self, **kwargs):
        assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
            'Invalid arguments passed to constructor: %s' % \
            ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        self.fb_emergency = kwargs.get('fb_emergency', int())
        self.fb_reverselight = kwargs.get('fb_reverselight', int())
        self.fb_rightsignal = kwargs.get('fb_rightsignal', int())
        self.fb_windowresistance = kwargs.get('fb_windowresistance', int())
        self.fb_leftsignal = kwargs.get('fb_leftsignal', int())
        self.fb_interiorlight = kwargs.get('fb_interiorlight', int())
        self.fb_drl = kwargs.get('fb_drl', int())
        self.fb_doorkeystatus = kwargs.get('fb_doorkeystatus', int())
        self.fb_brakelight = kwargs.get('fb_brakelight', int())
        self.fb_batteryvoltage = kwargs.get('fb_batteryvoltage', int())
        self.fb_chargeinput = kwargs.get('fb_chargeinput', int())
        self.fb_highbeam = kwargs.get('fb_highbeam', int())
        self.fb_lowbeam = kwargs.get('fb_lowbeam', int())
        self.fb_ignition = kwargs.get('fb_ignition', int())
        self.fb_hazardouslight = kwargs.get('fb_hazardouslight', int())
        self.fb_vehiclestatus = kwargs.get('fb_vehiclestatus', int())
        self.fb_leftdoorstatus = kwargs.get('fb_leftdoorstatus', int())
        self.fb_rightdoorstatus = kwargs.get('fb_rightdoorstatus', int())
        self.fb_batterysoc = kwargs.get('fb_batterysoc', int())
        self.fb_errorpowertrain = kwargs.get('fb_errorpowertrain', int())
        self.fb_errorbattery = kwargs.get('fb_errorbattery', int())
        self.fb_brakepedal_voltage_en = kwargs.get('fb_brakepedal_voltage_en', int())

    def __repr__(self):
        typename = self.__class__.__module__.split('.')
        typename.pop()
        typename.append(self.__class__.__name__)
        args = []
        for s, t in zip(self.__slots__, self.SLOT_TYPES):
            field = getattr(self, s)
            fieldstr = repr(field)
            # We use Python array type for fields that can be directly stored
            # in them, and "normal" sequences for everything else.  If it is
            # a type that we store in an array, strip off the 'array' portion.
            if (
                isinstance(t, rosidl_parser.definition.AbstractSequence) and
                isinstance(t.value_type, rosidl_parser.definition.BasicType) and
                t.value_type.typename in ['float', 'double', 'int8', 'uint8', 'int16', 'uint16', 'int32', 'uint32', 'int64', 'uint64']
            ):
                if len(field) == 0:
                    fieldstr = '[]'
                else:
                    assert fieldstr.startswith('array(')
                    prefix = "array('X', "
                    suffix = ')'
                    fieldstr = fieldstr[len(prefix):-len(suffix)]
            args.append(s[1:] + '=' + fieldstr)
        return '%s(%s)' % ('.'.join(typename), ', '.join(args))

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if self.fb_emergency != other.fb_emergency:
            return False
        if self.fb_reverselight != other.fb_reverselight:
            return False
        if self.fb_rightsignal != other.fb_rightsignal:
            return False
        if self.fb_windowresistance != other.fb_windowresistance:
            return False
        if self.fb_leftsignal != other.fb_leftsignal:
            return False
        if self.fb_interiorlight != other.fb_interiorlight:
            return False
        if self.fb_drl != other.fb_drl:
            return False
        if self.fb_doorkeystatus != other.fb_doorkeystatus:
            return False
        if self.fb_brakelight != other.fb_brakelight:
            return False
        if self.fb_batteryvoltage != other.fb_batteryvoltage:
            return False
        if self.fb_chargeinput != other.fb_chargeinput:
            return False
        if self.fb_highbeam != other.fb_highbeam:
            return False
        if self.fb_lowbeam != other.fb_lowbeam:
            return False
        if self.fb_ignition != other.fb_ignition:
            return False
        if self.fb_hazardouslight != other.fb_hazardouslight:
            return False
        if self.fb_vehiclestatus != other.fb_vehiclestatus:
            return False
        if self.fb_leftdoorstatus != other.fb_leftdoorstatus:
            return False
        if self.fb_rightdoorstatus != other.fb_rightdoorstatus:
            return False
        if self.fb_batterysoc != other.fb_batterysoc:
            return False
        if self.fb_errorpowertrain != other.fb_errorpowertrain:
            return False
        if self.fb_errorbattery != other.fb_errorbattery:
            return False
        if self.fb_brakepedal_voltage_en != other.fb_brakepedal_voltage_en:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @builtins.property
    def fb_emergency(self):
        """Message field 'fb_emergency'."""
        return self._fb_emergency

    @fb_emergency.setter
    def fb_emergency(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'fb_emergency' field must be of type 'int'"
            assert value >= 0 and value < 256, \
                "The 'fb_emergency' field must be an unsigned integer in [0, 255]"
        self._fb_emergency = value

    @builtins.property
    def fb_reverselight(self):
        """Message field 'fb_reverselight'."""
        return self._fb_reverselight

    @fb_reverselight.setter
    def fb_reverselight(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'fb_reverselight' field must be of type 'int'"
            assert value >= 0 and value < 256, \
                "The 'fb_reverselight' field must be an unsigned integer in [0, 255]"
        self._fb_reverselight = value

    @builtins.property
    def fb_rightsignal(self):
        """Message field 'fb_rightsignal'."""
        return self._fb_rightsignal

    @fb_rightsignal.setter
    def fb_rightsignal(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'fb_rightsignal' field must be of type 'int'"
            assert value >= 0 and value < 256, \
                "The 'fb_rightsignal' field must be an unsigned integer in [0, 255]"
        self._fb_rightsignal = value

    @builtins.property
    def fb_windowresistance(self):
        """Message field 'fb_windowresistance'."""
        return self._fb_windowresistance

    @fb_windowresistance.setter
    def fb_windowresistance(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'fb_windowresistance' field must be of type 'int'"
            assert value >= 0 and value < 256, \
                "The 'fb_windowresistance' field must be an unsigned integer in [0, 255]"
        self._fb_windowresistance = value

    @builtins.property
    def fb_leftsignal(self):
        """Message field 'fb_leftsignal'."""
        return self._fb_leftsignal

    @fb_leftsignal.setter
    def fb_leftsignal(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'fb_leftsignal' field must be of type 'int'"
            assert value >= 0 and value < 256, \
                "The 'fb_leftsignal' field must be an unsigned integer in [0, 255]"
        self._fb_leftsignal = value

    @builtins.property
    def fb_interiorlight(self):
        """Message field 'fb_interiorlight'."""
        return self._fb_interiorlight

    @fb_interiorlight.setter
    def fb_interiorlight(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'fb_interiorlight' field must be of type 'int'"
            assert value >= 0 and value < 256, \
                "The 'fb_interiorlight' field must be an unsigned integer in [0, 255]"
        self._fb_interiorlight = value

    @builtins.property
    def fb_drl(self):
        """Message field 'fb_drl'."""
        return self._fb_drl

    @fb_drl.setter
    def fb_drl(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'fb_drl' field must be of type 'int'"
            assert value >= 0 and value < 256, \
                "The 'fb_drl' field must be an unsigned integer in [0, 255]"
        self._fb_drl = value

    @builtins.property
    def fb_doorkeystatus(self):
        """Message field 'fb_doorkeystatus'."""
        return self._fb_doorkeystatus

    @fb_doorkeystatus.setter
    def fb_doorkeystatus(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'fb_doorkeystatus' field must be of type 'int'"
            assert value >= 0 and value < 256, \
                "The 'fb_doorkeystatus' field must be an unsigned integer in [0, 255]"
        self._fb_doorkeystatus = value

    @builtins.property
    def fb_brakelight(self):
        """Message field 'fb_brakelight'."""
        return self._fb_brakelight

    @fb_brakelight.setter
    def fb_brakelight(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'fb_brakelight' field must be of type 'int'"
            assert value >= 0 and value < 256, \
                "The 'fb_brakelight' field must be an unsigned integer in [0, 255]"
        self._fb_brakelight = value

    @builtins.property
    def fb_batteryvoltage(self):
        """Message field 'fb_batteryvoltage'."""
        return self._fb_batteryvoltage

    @fb_batteryvoltage.setter
    def fb_batteryvoltage(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'fb_batteryvoltage' field must be of type 'int'"
            assert value >= 0 and value < 256, \
                "The 'fb_batteryvoltage' field must be an unsigned integer in [0, 255]"
        self._fb_batteryvoltage = value

    @builtins.property
    def fb_chargeinput(self):
        """Message field 'fb_chargeinput'."""
        return self._fb_chargeinput

    @fb_chargeinput.setter
    def fb_chargeinput(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'fb_chargeinput' field must be of type 'int'"
            assert value >= 0 and value < 256, \
                "The 'fb_chargeinput' field must be an unsigned integer in [0, 255]"
        self._fb_chargeinput = value

    @builtins.property
    def fb_highbeam(self):
        """Message field 'fb_highbeam'."""
        return self._fb_highbeam

    @fb_highbeam.setter
    def fb_highbeam(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'fb_highbeam' field must be of type 'int'"
            assert value >= 0 and value < 256, \
                "The 'fb_highbeam' field must be an unsigned integer in [0, 255]"
        self._fb_highbeam = value

    @builtins.property
    def fb_lowbeam(self):
        """Message field 'fb_lowbeam'."""
        return self._fb_lowbeam

    @fb_lowbeam.setter
    def fb_lowbeam(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'fb_lowbeam' field must be of type 'int'"
            assert value >= 0 and value < 256, \
                "The 'fb_lowbeam' field must be an unsigned integer in [0, 255]"
        self._fb_lowbeam = value

    @builtins.property
    def fb_ignition(self):
        """Message field 'fb_ignition'."""
        return self._fb_ignition

    @fb_ignition.setter
    def fb_ignition(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'fb_ignition' field must be of type 'int'"
            assert value >= 0 and value < 256, \
                "The 'fb_ignition' field must be an unsigned integer in [0, 255]"
        self._fb_ignition = value

    @builtins.property
    def fb_hazardouslight(self):
        """Message field 'fb_hazardouslight'."""
        return self._fb_hazardouslight

    @fb_hazardouslight.setter
    def fb_hazardouslight(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'fb_hazardouslight' field must be of type 'int'"
            assert value >= 0 and value < 256, \
                "The 'fb_hazardouslight' field must be an unsigned integer in [0, 255]"
        self._fb_hazardouslight = value

    @builtins.property
    def fb_vehiclestatus(self):
        """Message field 'fb_vehiclestatus'."""
        return self._fb_vehiclestatus

    @fb_vehiclestatus.setter
    def fb_vehiclestatus(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'fb_vehiclestatus' field must be of type 'int'"
            assert value >= 0 and value < 256, \
                "The 'fb_vehiclestatus' field must be an unsigned integer in [0, 255]"
        self._fb_vehiclestatus = value

    @builtins.property
    def fb_leftdoorstatus(self):
        """Message field 'fb_leftdoorstatus'."""
        return self._fb_leftdoorstatus

    @fb_leftdoorstatus.setter
    def fb_leftdoorstatus(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'fb_leftdoorstatus' field must be of type 'int'"
            assert value >= 0 and value < 256, \
                "The 'fb_leftdoorstatus' field must be an unsigned integer in [0, 255]"
        self._fb_leftdoorstatus = value

    @builtins.property
    def fb_rightdoorstatus(self):
        """Message field 'fb_rightdoorstatus'."""
        return self._fb_rightdoorstatus

    @fb_rightdoorstatus.setter
    def fb_rightdoorstatus(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'fb_rightdoorstatus' field must be of type 'int'"
            assert value >= 0 and value < 256, \
                "The 'fb_rightdoorstatus' field must be an unsigned integer in [0, 255]"
        self._fb_rightdoorstatus = value

    @builtins.property
    def fb_batterysoc(self):
        """Message field 'fb_batterysoc'."""
        return self._fb_batterysoc

    @fb_batterysoc.setter
    def fb_batterysoc(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'fb_batterysoc' field must be of type 'int'"
            assert value >= 0 and value < 256, \
                "The 'fb_batterysoc' field must be an unsigned integer in [0, 255]"
        self._fb_batterysoc = value

    @builtins.property
    def fb_errorpowertrain(self):
        """Message field 'fb_errorpowertrain'."""
        return self._fb_errorpowertrain

    @fb_errorpowertrain.setter
    def fb_errorpowertrain(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'fb_errorpowertrain' field must be of type 'int'"
            assert value >= 0 and value < 256, \
                "The 'fb_errorpowertrain' field must be an unsigned integer in [0, 255]"
        self._fb_errorpowertrain = value

    @builtins.property
    def fb_errorbattery(self):
        """Message field 'fb_errorbattery'."""
        return self._fb_errorbattery

    @fb_errorbattery.setter
    def fb_errorbattery(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'fb_errorbattery' field must be of type 'int'"
            assert value >= 0 and value < 256, \
                "The 'fb_errorbattery' field must be an unsigned integer in [0, 255]"
        self._fb_errorbattery = value

    @builtins.property
    def fb_brakepedal_voltage_en(self):
        """Message field 'fb_brakepedal_voltage_en'."""
        return self._fb_brakepedal_voltage_en

    @fb_brakepedal_voltage_en.setter
    def fb_brakepedal_voltage_en(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'fb_brakepedal_voltage_en' field must be of type 'int'"
            assert value >= 0 and value < 256, \
                "The 'fb_brakepedal_voltage_en' field must be an unsigned integer in [0, 255]"
        self._fb_brakepedal_voltage_en = value
