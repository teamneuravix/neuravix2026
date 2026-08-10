# generated from rosidl_generator_py/resource/_idl.py.em
# with input from smart_can_msgs:msg/Autonomoussteeringmotcontrol.idl
# generated code does not contain a copyright notice


# Import statements for member types

import builtins  # noqa: E402, I100

import rosidl_parser.definition  # noqa: E402, I100


class Metaclass_Autonomoussteeringmotcontrol(type):
    """Metaclass of message 'Autonomoussteeringmotcontrol'."""

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
                'smart_can_msgs.msg.Autonomoussteeringmotcontrol')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__msg__autonomoussteeringmotcontrol
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__msg__autonomoussteeringmotcontrol
            cls._CONVERT_TO_PY = module.convert_to_py_msg__msg__autonomoussteeringmotcontrol
            cls._TYPE_SUPPORT = module.type_support_msg__msg__autonomoussteeringmotcontrol
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__msg__autonomoussteeringmotcontrol

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
        }


class Autonomoussteeringmotcontrol(metaclass=Metaclass_Autonomoussteeringmotcontrol):
    """Message class 'Autonomoussteeringmotcontrol'."""

    __slots__ = [
        '_autonomous_steeringmot_en',
        '_autonomous_steeringmot_pwm',
    ]

    _fields_and_field_types = {
        'autonomous_steeringmot_en': 'uint8',
        'autonomous_steeringmot_pwm': 'uint8',
    }

    SLOT_TYPES = (
        rosidl_parser.definition.BasicType('uint8'),  # noqa: E501
        rosidl_parser.definition.BasicType('uint8'),  # noqa: E501
    )

    def __init__(self, **kwargs):
        assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
            'Invalid arguments passed to constructor: %s' % \
            ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        self.autonomous_steeringmot_en = kwargs.get('autonomous_steeringmot_en', int())
        self.autonomous_steeringmot_pwm = kwargs.get('autonomous_steeringmot_pwm', int())

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
        if self.autonomous_steeringmot_en != other.autonomous_steeringmot_en:
            return False
        if self.autonomous_steeringmot_pwm != other.autonomous_steeringmot_pwm:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @builtins.property
    def autonomous_steeringmot_en(self):
        """Message field 'autonomous_steeringmot_en'."""
        return self._autonomous_steeringmot_en

    @autonomous_steeringmot_en.setter
    def autonomous_steeringmot_en(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'autonomous_steeringmot_en' field must be of type 'int'"
            assert value >= 0 and value < 256, \
                "The 'autonomous_steeringmot_en' field must be an unsigned integer in [0, 255]"
        self._autonomous_steeringmot_en = value

    @builtins.property
    def autonomous_steeringmot_pwm(self):
        """Message field 'autonomous_steeringmot_pwm'."""
        return self._autonomous_steeringmot_pwm

    @autonomous_steeringmot_pwm.setter
    def autonomous_steeringmot_pwm(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'autonomous_steeringmot_pwm' field must be of type 'int'"
            assert value >= 0 and value < 256, \
                "The 'autonomous_steeringmot_pwm' field must be an unsigned integer in [0, 255]"
        self._autonomous_steeringmot_pwm = value
