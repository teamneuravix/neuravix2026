# generated from rosidl_generator_py/resource/_idl.py.em
# with input from smart_can_msgs:msg/Sndrcunitbrakedata.idl
# generated code does not contain a copyright notice


# Import statements for member types

import builtins  # noqa: E402, I100

import rosidl_parser.definition  # noqa: E402, I100


class Metaclass_Sndrcunitbrakedata(type):
    """Metaclass of message 'Sndrcunitbrakedata'."""

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
                'smart_can_msgs.msg.Sndrcunitbrakedata')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__msg__sndrcunitbrakedata
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__msg__sndrcunitbrakedata
            cls._CONVERT_TO_PY = module.convert_to_py_msg__msg__sndrcunitbrakedata
            cls._TYPE_SUPPORT = module.type_support_msg__msg__sndrcunitbrakedata
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__msg__sndrcunitbrakedata

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
        }


class Sndrcunitbrakedata(metaclass=Metaclass_Sndrcunitbrakedata):
    """Message class 'Sndrcunitbrakedata'."""

    __slots__ = [
        '_rc_brakepedal_speed',
        '_rc_brakepedal_acc',
        '_rc_brakepedal_pos',
    ]

    _fields_and_field_types = {
        'rc_brakepedal_speed': 'uint16',
        'rc_brakepedal_acc': 'uint16',
        'rc_brakepedal_pos': 'uint8',
    }

    SLOT_TYPES = (
        rosidl_parser.definition.BasicType('uint16'),  # noqa: E501
        rosidl_parser.definition.BasicType('uint16'),  # noqa: E501
        rosidl_parser.definition.BasicType('uint8'),  # noqa: E501
    )

    def __init__(self, **kwargs):
        assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
            'Invalid arguments passed to constructor: %s' % \
            ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        self.rc_brakepedal_speed = kwargs.get('rc_brakepedal_speed', int())
        self.rc_brakepedal_acc = kwargs.get('rc_brakepedal_acc', int())
        self.rc_brakepedal_pos = kwargs.get('rc_brakepedal_pos', int())

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
        if self.rc_brakepedal_speed != other.rc_brakepedal_speed:
            return False
        if self.rc_brakepedal_acc != other.rc_brakepedal_acc:
            return False
        if self.rc_brakepedal_pos != other.rc_brakepedal_pos:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @builtins.property
    def rc_brakepedal_speed(self):
        """Message field 'rc_brakepedal_speed'."""
        return self._rc_brakepedal_speed

    @rc_brakepedal_speed.setter
    def rc_brakepedal_speed(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'rc_brakepedal_speed' field must be of type 'int'"
            assert value >= 0 and value < 65536, \
                "The 'rc_brakepedal_speed' field must be an unsigned integer in [0, 65535]"
        self._rc_brakepedal_speed = value

    @builtins.property
    def rc_brakepedal_acc(self):
        """Message field 'rc_brakepedal_acc'."""
        return self._rc_brakepedal_acc

    @rc_brakepedal_acc.setter
    def rc_brakepedal_acc(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'rc_brakepedal_acc' field must be of type 'int'"
            assert value >= 0 and value < 65536, \
                "The 'rc_brakepedal_acc' field must be an unsigned integer in [0, 65535]"
        self._rc_brakepedal_acc = value

    @builtins.property
    def rc_brakepedal_pos(self):
        """Message field 'rc_brakepedal_pos'."""
        return self._rc_brakepedal_pos

    @rc_brakepedal_pos.setter
    def rc_brakepedal_pos(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'rc_brakepedal_pos' field must be of type 'int'"
            assert value >= 0 and value < 256, \
                "The 'rc_brakepedal_pos' field must be an unsigned integer in [0, 255]"
        self._rc_brakepedal_pos = value
