# generated from rosidl_generator_py/resource/_idl.py.em
# with input from smart_can_msgs:msg/Rcthrtdata.idl
# generated code does not contain a copyright notice


# Import statements for member types

import builtins  # noqa: E402, I100

import rosidl_parser.definition  # noqa: E402, I100


class Metaclass_Rcthrtdata(type):
    """Metaclass of message 'Rcthrtdata'."""

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
                'smart_can_msgs.msg.Rcthrtdata')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__msg__rcthrtdata
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__msg__rcthrtdata
            cls._CONVERT_TO_PY = module.convert_to_py_msg__msg__rcthrtdata
            cls._TYPE_SUPPORT = module.type_support_msg__msg__rcthrtdata
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__msg__rcthrtdata

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
        }


class Rcthrtdata(metaclass=Metaclass_Rcthrtdata):
    """Message class 'Rcthrtdata'."""

    __slots__ = [
        '_rc_thrt_pedal_position',
        '_rc_thrt_pedal_press',
    ]

    _fields_and_field_types = {
        'rc_thrt_pedal_position': 'uint8',
        'rc_thrt_pedal_press': 'uint8',
    }

    SLOT_TYPES = (
        rosidl_parser.definition.BasicType('uint8'),  # noqa: E501
        rosidl_parser.definition.BasicType('uint8'),  # noqa: E501
    )

    def __init__(self, **kwargs):
        assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
            'Invalid arguments passed to constructor: %s' % \
            ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        self.rc_thrt_pedal_position = kwargs.get('rc_thrt_pedal_position', int())
        self.rc_thrt_pedal_press = kwargs.get('rc_thrt_pedal_press', int())

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
        if self.rc_thrt_pedal_position != other.rc_thrt_pedal_position:
            return False
        if self.rc_thrt_pedal_press != other.rc_thrt_pedal_press:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @builtins.property
    def rc_thrt_pedal_position(self):
        """Message field 'rc_thrt_pedal_position'."""
        return self._rc_thrt_pedal_position

    @rc_thrt_pedal_position.setter
    def rc_thrt_pedal_position(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'rc_thrt_pedal_position' field must be of type 'int'"
            assert value >= 0 and value < 256, \
                "The 'rc_thrt_pedal_position' field must be an unsigned integer in [0, 255]"
        self._rc_thrt_pedal_position = value

    @builtins.property
    def rc_thrt_pedal_press(self):
        """Message field 'rc_thrt_pedal_press'."""
        return self._rc_thrt_pedal_press

    @rc_thrt_pedal_press.setter
    def rc_thrt_pedal_press(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'rc_thrt_pedal_press' field must be of type 'int'"
            assert value >= 0 and value < 256, \
                "The 'rc_thrt_pedal_press' field must be an unsigned integer in [0, 255]"
        self._rc_thrt_pedal_press = value
