# generated from rosidl_generator_py/resource/_idl.py.em
# with input from smart_can_msgs:msg/Sndrcunitsteeringdata.idl
# generated code does not contain a copyright notice


# Import statements for member types

import builtins  # noqa: E402, I100

import rosidl_parser.definition  # noqa: E402, I100


class Metaclass_Sndrcunitsteeringdata(type):
    """Metaclass of message 'Sndrcunitsteeringdata'."""

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
                'smart_can_msgs.msg.Sndrcunitsteeringdata')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__msg__sndrcunitsteeringdata
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__msg__sndrcunitsteeringdata
            cls._CONVERT_TO_PY = module.convert_to_py_msg__msg__sndrcunitsteeringdata
            cls._TYPE_SUPPORT = module.type_support_msg__msg__sndrcunitsteeringdata
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__msg__sndrcunitsteeringdata

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
        }


class Sndrcunitsteeringdata(metaclass=Metaclass_Sndrcunitsteeringdata):
    """Message class 'Sndrcunitsteeringdata'."""

    __slots__ = [
        '_rc_steering_rightlimit',
        '_rc_steering_leftlimit',
        '_rc_steeringpwm',
        '_rc_steeringdirection',
    ]

    _fields_and_field_types = {
        'rc_steering_rightlimit': 'uint8',
        'rc_steering_leftlimit': 'uint8',
        'rc_steeringpwm': 'uint16',
        'rc_steeringdirection': 'uint8',
    }

    SLOT_TYPES = (
        rosidl_parser.definition.BasicType('uint8'),  # noqa: E501
        rosidl_parser.definition.BasicType('uint8'),  # noqa: E501
        rosidl_parser.definition.BasicType('uint16'),  # noqa: E501
        rosidl_parser.definition.BasicType('uint8'),  # noqa: E501
    )

    def __init__(self, **kwargs):
        assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
            'Invalid arguments passed to constructor: %s' % \
            ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        self.rc_steering_rightlimit = kwargs.get('rc_steering_rightlimit', int())
        self.rc_steering_leftlimit = kwargs.get('rc_steering_leftlimit', int())
        self.rc_steeringpwm = kwargs.get('rc_steeringpwm', int())
        self.rc_steeringdirection = kwargs.get('rc_steeringdirection', int())

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
        if self.rc_steering_rightlimit != other.rc_steering_rightlimit:
            return False
        if self.rc_steering_leftlimit != other.rc_steering_leftlimit:
            return False
        if self.rc_steeringpwm != other.rc_steeringpwm:
            return False
        if self.rc_steeringdirection != other.rc_steeringdirection:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @builtins.property
    def rc_steering_rightlimit(self):
        """Message field 'rc_steering_rightlimit'."""
        return self._rc_steering_rightlimit

    @rc_steering_rightlimit.setter
    def rc_steering_rightlimit(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'rc_steering_rightlimit' field must be of type 'int'"
            assert value >= 0 and value < 256, \
                "The 'rc_steering_rightlimit' field must be an unsigned integer in [0, 255]"
        self._rc_steering_rightlimit = value

    @builtins.property
    def rc_steering_leftlimit(self):
        """Message field 'rc_steering_leftlimit'."""
        return self._rc_steering_leftlimit

    @rc_steering_leftlimit.setter
    def rc_steering_leftlimit(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'rc_steering_leftlimit' field must be of type 'int'"
            assert value >= 0 and value < 256, \
                "The 'rc_steering_leftlimit' field must be an unsigned integer in [0, 255]"
        self._rc_steering_leftlimit = value

    @builtins.property
    def rc_steeringpwm(self):
        """Message field 'rc_steeringpwm'."""
        return self._rc_steeringpwm

    @rc_steeringpwm.setter
    def rc_steeringpwm(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'rc_steeringpwm' field must be of type 'int'"
            assert value >= 0 and value < 65536, \
                "The 'rc_steeringpwm' field must be an unsigned integer in [0, 65535]"
        self._rc_steeringpwm = value

    @builtins.property
    def rc_steeringdirection(self):
        """Message field 'rc_steeringdirection'."""
        return self._rc_steeringdirection

    @rc_steeringdirection.setter
    def rc_steeringdirection(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'rc_steeringdirection' field must be of type 'int'"
            assert value >= 0 and value < 256, \
                "The 'rc_steeringdirection' field must be an unsigned integer in [0, 255]"
        self._rc_steeringdirection = value
