# generated from rosidl_generator_py/resource/_idl.py.em
# with input from smart_can_msgs:msg/Sndrcunithandbrakedata.idl
# generated code does not contain a copyright notice


# Import statements for member types

import builtins  # noqa: E402, I100

import rosidl_parser.definition  # noqa: E402, I100


class Metaclass_Sndrcunithandbrakedata(type):
    """Metaclass of message 'Sndrcunithandbrakedata'."""

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
                'smart_can_msgs.msg.Sndrcunithandbrakedata')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__msg__sndrcunithandbrakedata
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__msg__sndrcunithandbrakedata
            cls._CONVERT_TO_PY = module.convert_to_py_msg__msg__sndrcunithandbrakedata
            cls._TYPE_SUPPORT = module.type_support_msg__msg__sndrcunithandbrakedata
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__msg__sndrcunithandbrakedata

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
        }


class Sndrcunithandbrakedata(metaclass=Metaclass_Sndrcunithandbrakedata):
    """Message class 'Sndrcunithandbrakedata'."""

    __slots__ = [
        '_rc_hb_pwmvalue',
        '_rc_handbrake_press',
        '_rc_handbrake_free',
        '_rc_handbrakedata',
    ]

    _fields_and_field_types = {
        'rc_hb_pwmvalue': 'uint16',
        'rc_handbrake_press': 'uint8',
        'rc_handbrake_free': 'uint8',
        'rc_handbrakedata': 'uint8',
    }

    SLOT_TYPES = (
        rosidl_parser.definition.BasicType('uint16'),  # noqa: E501
        rosidl_parser.definition.BasicType('uint8'),  # noqa: E501
        rosidl_parser.definition.BasicType('uint8'),  # noqa: E501
        rosidl_parser.definition.BasicType('uint8'),  # noqa: E501
    )

    def __init__(self, **kwargs):
        assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
            'Invalid arguments passed to constructor: %s' % \
            ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        self.rc_hb_pwmvalue = kwargs.get('rc_hb_pwmvalue', int())
        self.rc_handbrake_press = kwargs.get('rc_handbrake_press', int())
        self.rc_handbrake_free = kwargs.get('rc_handbrake_free', int())
        self.rc_handbrakedata = kwargs.get('rc_handbrakedata', int())

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
        if self.rc_hb_pwmvalue != other.rc_hb_pwmvalue:
            return False
        if self.rc_handbrake_press != other.rc_handbrake_press:
            return False
        if self.rc_handbrake_free != other.rc_handbrake_free:
            return False
        if self.rc_handbrakedata != other.rc_handbrakedata:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @builtins.property
    def rc_hb_pwmvalue(self):
        """Message field 'rc_hb_pwmvalue'."""
        return self._rc_hb_pwmvalue

    @rc_hb_pwmvalue.setter
    def rc_hb_pwmvalue(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'rc_hb_pwmvalue' field must be of type 'int'"
            assert value >= 0 and value < 65536, \
                "The 'rc_hb_pwmvalue' field must be an unsigned integer in [0, 65535]"
        self._rc_hb_pwmvalue = value

    @builtins.property
    def rc_handbrake_press(self):
        """Message field 'rc_handbrake_press'."""
        return self._rc_handbrake_press

    @rc_handbrake_press.setter
    def rc_handbrake_press(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'rc_handbrake_press' field must be of type 'int'"
            assert value >= 0 and value < 256, \
                "The 'rc_handbrake_press' field must be an unsigned integer in [0, 255]"
        self._rc_handbrake_press = value

    @builtins.property
    def rc_handbrake_free(self):
        """Message field 'rc_handbrake_free'."""
        return self._rc_handbrake_free

    @rc_handbrake_free.setter
    def rc_handbrake_free(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'rc_handbrake_free' field must be of type 'int'"
            assert value >= 0 and value < 256, \
                "The 'rc_handbrake_free' field must be an unsigned integer in [0, 255]"
        self._rc_handbrake_free = value

    @builtins.property
    def rc_handbrakedata(self):
        """Message field 'rc_handbrakedata'."""
        return self._rc_handbrakedata

    @rc_handbrakedata.setter
    def rc_handbrakedata(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'rc_handbrakedata' field must be of type 'int'"
            assert value >= 0 and value < 256, \
                "The 'rc_handbrakedata' field must be an unsigned integer in [0, 255]"
        self._rc_handbrakedata = value
