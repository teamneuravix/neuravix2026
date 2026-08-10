# generated from rosidl_generator_py/resource/_idl.py.em
# with input from smart_can_msgs:msg/Rcunittoomux.idl
# generated code does not contain a copyright notice


# Import statements for member types

import builtins  # noqa: E402, I100

import rosidl_parser.definition  # noqa: E402, I100


class Metaclass_Rcunittoomux(type):
    """Metaclass of message 'Rcunittoomux'."""

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
                'smart_can_msgs.msg.Rcunittoomux')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__msg__rcunittoomux
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__msg__rcunittoomux
            cls._CONVERT_TO_PY = module.convert_to_py_msg__msg__rcunittoomux
            cls._TYPE_SUPPORT = module.type_support_msg__msg__rcunittoomux
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__msg__rcunittoomux

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
        }


class Rcunittoomux(metaclass=Metaclass_Rcunittoomux):
    """Message class 'Rcunittoomux'."""

    __slots__ = [
        '_autonomous_emergency',
        '_rc_windowresintance',
        '_rc_interiorlight',
        '_rc_reverselight',
        '_rc_drl',
        '_rc_brakelight',
        '_autonomous_door_open',
        '_autonomous_door_close',
        '_rc_signalstatus',
        '_rc_lowbeam',
        '_rc_highbeam',
        '_rc_selectiongear',
        '_rc_ignition',
    ]

    _fields_and_field_types = {
        'autonomous_emergency': 'int8',
        'rc_windowresintance': 'uint8',
        'rc_interiorlight': 'uint8',
        'rc_reverselight': 'uint8',
        'rc_drl': 'uint8',
        'rc_brakelight': 'uint8',
        'autonomous_door_open': 'int8',
        'autonomous_door_close': 'int8',
        'rc_signalstatus': 'uint8',
        'rc_lowbeam': 'uint8',
        'rc_highbeam': 'uint8',
        'rc_selectiongear': 'uint8',
        'rc_ignition': 'uint8',
    }

    SLOT_TYPES = (
        rosidl_parser.definition.BasicType('int8'),  # noqa: E501
        rosidl_parser.definition.BasicType('uint8'),  # noqa: E501
        rosidl_parser.definition.BasicType('uint8'),  # noqa: E501
        rosidl_parser.definition.BasicType('uint8'),  # noqa: E501
        rosidl_parser.definition.BasicType('uint8'),  # noqa: E501
        rosidl_parser.definition.BasicType('uint8'),  # noqa: E501
        rosidl_parser.definition.BasicType('int8'),  # noqa: E501
        rosidl_parser.definition.BasicType('int8'),  # noqa: E501
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
        self.autonomous_emergency = kwargs.get('autonomous_emergency', int())
        self.rc_windowresintance = kwargs.get('rc_windowresintance', int())
        self.rc_interiorlight = kwargs.get('rc_interiorlight', int())
        self.rc_reverselight = kwargs.get('rc_reverselight', int())
        self.rc_drl = kwargs.get('rc_drl', int())
        self.rc_brakelight = kwargs.get('rc_brakelight', int())
        self.autonomous_door_open = kwargs.get('autonomous_door_open', int())
        self.autonomous_door_close = kwargs.get('autonomous_door_close', int())
        self.rc_signalstatus = kwargs.get('rc_signalstatus', int())
        self.rc_lowbeam = kwargs.get('rc_lowbeam', int())
        self.rc_highbeam = kwargs.get('rc_highbeam', int())
        self.rc_selectiongear = kwargs.get('rc_selectiongear', int())
        self.rc_ignition = kwargs.get('rc_ignition', int())

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
        if self.autonomous_emergency != other.autonomous_emergency:
            return False
        if self.rc_windowresintance != other.rc_windowresintance:
            return False
        if self.rc_interiorlight != other.rc_interiorlight:
            return False
        if self.rc_reverselight != other.rc_reverselight:
            return False
        if self.rc_drl != other.rc_drl:
            return False
        if self.rc_brakelight != other.rc_brakelight:
            return False
        if self.autonomous_door_open != other.autonomous_door_open:
            return False
        if self.autonomous_door_close != other.autonomous_door_close:
            return False
        if self.rc_signalstatus != other.rc_signalstatus:
            return False
        if self.rc_lowbeam != other.rc_lowbeam:
            return False
        if self.rc_highbeam != other.rc_highbeam:
            return False
        if self.rc_selectiongear != other.rc_selectiongear:
            return False
        if self.rc_ignition != other.rc_ignition:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @builtins.property
    def autonomous_emergency(self):
        """Message field 'autonomous_emergency'."""
        return self._autonomous_emergency

    @autonomous_emergency.setter
    def autonomous_emergency(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'autonomous_emergency' field must be of type 'int'"
            assert value >= -128 and value < 128, \
                "The 'autonomous_emergency' field must be an integer in [-128, 127]"
        self._autonomous_emergency = value

    @builtins.property
    def rc_windowresintance(self):
        """Message field 'rc_windowresintance'."""
        return self._rc_windowresintance

    @rc_windowresintance.setter
    def rc_windowresintance(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'rc_windowresintance' field must be of type 'int'"
            assert value >= 0 and value < 256, \
                "The 'rc_windowresintance' field must be an unsigned integer in [0, 255]"
        self._rc_windowresintance = value

    @builtins.property
    def rc_interiorlight(self):
        """Message field 'rc_interiorlight'."""
        return self._rc_interiorlight

    @rc_interiorlight.setter
    def rc_interiorlight(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'rc_interiorlight' field must be of type 'int'"
            assert value >= 0 and value < 256, \
                "The 'rc_interiorlight' field must be an unsigned integer in [0, 255]"
        self._rc_interiorlight = value

    @builtins.property
    def rc_reverselight(self):
        """Message field 'rc_reverselight'."""
        return self._rc_reverselight

    @rc_reverselight.setter
    def rc_reverselight(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'rc_reverselight' field must be of type 'int'"
            assert value >= 0 and value < 256, \
                "The 'rc_reverselight' field must be an unsigned integer in [0, 255]"
        self._rc_reverselight = value

    @builtins.property
    def rc_drl(self):
        """Message field 'rc_drl'."""
        return self._rc_drl

    @rc_drl.setter
    def rc_drl(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'rc_drl' field must be of type 'int'"
            assert value >= 0 and value < 256, \
                "The 'rc_drl' field must be an unsigned integer in [0, 255]"
        self._rc_drl = value

    @builtins.property
    def rc_brakelight(self):
        """Message field 'rc_brakelight'."""
        return self._rc_brakelight

    @rc_brakelight.setter
    def rc_brakelight(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'rc_brakelight' field must be of type 'int'"
            assert value >= 0 and value < 256, \
                "The 'rc_brakelight' field must be an unsigned integer in [0, 255]"
        self._rc_brakelight = value

    @builtins.property
    def autonomous_door_open(self):
        """Message field 'autonomous_door_open'."""
        return self._autonomous_door_open

    @autonomous_door_open.setter
    def autonomous_door_open(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'autonomous_door_open' field must be of type 'int'"
            assert value >= -128 and value < 128, \
                "The 'autonomous_door_open' field must be an integer in [-128, 127]"
        self._autonomous_door_open = value

    @builtins.property
    def autonomous_door_close(self):
        """Message field 'autonomous_door_close'."""
        return self._autonomous_door_close

    @autonomous_door_close.setter
    def autonomous_door_close(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'autonomous_door_close' field must be of type 'int'"
            assert value >= -128 and value < 128, \
                "The 'autonomous_door_close' field must be an integer in [-128, 127]"
        self._autonomous_door_close = value

    @builtins.property
    def rc_signalstatus(self):
        """Message field 'rc_signalstatus'."""
        return self._rc_signalstatus

    @rc_signalstatus.setter
    def rc_signalstatus(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'rc_signalstatus' field must be of type 'int'"
            assert value >= 0 and value < 256, \
                "The 'rc_signalstatus' field must be an unsigned integer in [0, 255]"
        self._rc_signalstatus = value

    @builtins.property
    def rc_lowbeam(self):
        """Message field 'rc_lowbeam'."""
        return self._rc_lowbeam

    @rc_lowbeam.setter
    def rc_lowbeam(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'rc_lowbeam' field must be of type 'int'"
            assert value >= 0 and value < 256, \
                "The 'rc_lowbeam' field must be an unsigned integer in [0, 255]"
        self._rc_lowbeam = value

    @builtins.property
    def rc_highbeam(self):
        """Message field 'rc_highbeam'."""
        return self._rc_highbeam

    @rc_highbeam.setter
    def rc_highbeam(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'rc_highbeam' field must be of type 'int'"
            assert value >= 0 and value < 256, \
                "The 'rc_highbeam' field must be an unsigned integer in [0, 255]"
        self._rc_highbeam = value

    @builtins.property
    def rc_selectiongear(self):
        """Message field 'rc_selectiongear'."""
        return self._rc_selectiongear

    @rc_selectiongear.setter
    def rc_selectiongear(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'rc_selectiongear' field must be of type 'int'"
            assert value >= 0 and value < 256, \
                "The 'rc_selectiongear' field must be an unsigned integer in [0, 255]"
        self._rc_selectiongear = value

    @builtins.property
    def rc_ignition(self):
        """Message field 'rc_ignition'."""
        return self._rc_ignition

    @rc_ignition.setter
    def rc_ignition(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'rc_ignition' field must be of type 'int'"
            assert value >= 0 and value < 256, \
                "The 'rc_ignition' field must be an unsigned integer in [0, 255]"
        self._rc_ignition = value
