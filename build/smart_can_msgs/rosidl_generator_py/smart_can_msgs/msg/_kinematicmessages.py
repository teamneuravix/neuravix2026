# generated from rosidl_generator_py/resource/_idl.py.em
# with input from smart_can_msgs:msg/Kinematicmessages.idl
# generated code does not contain a copyright notice


# Import statements for member types

import builtins  # noqa: E402, I100

import math  # noqa: E402, I100

import rosidl_parser.definition  # noqa: E402, I100


class Metaclass_Kinematicmessages(type):
    """Metaclass of message 'Kinematicmessages'."""

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
                'smart_can_msgs.msg.Kinematicmessages')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__msg__kinematicmessages
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__msg__kinematicmessages
            cls._CONVERT_TO_PY = module.convert_to_py_msg__msg__kinematicmessages
            cls._TYPE_SUPPORT = module.type_support_msg__msg__kinematicmessages
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__msg__kinematicmessages

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
        }


class Kinematicmessages(metaclass=Metaclass_Kinematicmessages):
    """Message class 'Kinematicmessages'."""

    __slots__ = [
        '_joint_type',
        '_angle',
        '_angle_y',
        '_angular_velocity',
        '_link_length',
    ]

    _fields_and_field_types = {
        'joint_type': 'uint8',
        'angle': 'float',
        'angle_y': 'float',
        'angular_velocity': 'float',
        'link_length': 'float',
    }

    SLOT_TYPES = (
        rosidl_parser.definition.BasicType('uint8'),  # noqa: E501
        rosidl_parser.definition.BasicType('float'),  # noqa: E501
        rosidl_parser.definition.BasicType('float'),  # noqa: E501
        rosidl_parser.definition.BasicType('float'),  # noqa: E501
        rosidl_parser.definition.BasicType('float'),  # noqa: E501
    )

    def __init__(self, **kwargs):
        assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
            'Invalid arguments passed to constructor: %s' % \
            ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        self.joint_type = kwargs.get('joint_type', int())
        self.angle = kwargs.get('angle', float())
        self.angle_y = kwargs.get('angle_y', float())
        self.angular_velocity = kwargs.get('angular_velocity', float())
        self.link_length = kwargs.get('link_length', float())

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
        if self.joint_type != other.joint_type:
            return False
        if self.angle != other.angle:
            return False
        if self.angle_y != other.angle_y:
            return False
        if self.angular_velocity != other.angular_velocity:
            return False
        if self.link_length != other.link_length:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @builtins.property
    def joint_type(self):
        """Message field 'joint_type'."""
        return self._joint_type

    @joint_type.setter
    def joint_type(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'joint_type' field must be of type 'int'"
            assert value >= 0 and value < 256, \
                "The 'joint_type' field must be an unsigned integer in [0, 255]"
        self._joint_type = value

    @builtins.property
    def angle(self):
        """Message field 'angle'."""
        return self._angle

    @angle.setter
    def angle(self, value):
        if __debug__:
            assert \
                isinstance(value, float), \
                "The 'angle' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'angle' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._angle = value

    @builtins.property
    def angle_y(self):
        """Message field 'angle_y'."""
        return self._angle_y

    @angle_y.setter
    def angle_y(self, value):
        if __debug__:
            assert \
                isinstance(value, float), \
                "The 'angle_y' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'angle_y' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._angle_y = value

    @builtins.property
    def angular_velocity(self):
        """Message field 'angular_velocity'."""
        return self._angular_velocity

    @angular_velocity.setter
    def angular_velocity(self, value):
        if __debug__:
            assert \
                isinstance(value, float), \
                "The 'angular_velocity' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'angular_velocity' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._angular_velocity = value

    @builtins.property
    def link_length(self):
        """Message field 'link_length'."""
        return self._link_length

    @link_length.setter
    def link_length(self, value):
        if __debug__:
            assert \
                isinstance(value, float), \
                "The 'link_length' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'link_length' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._link_length = value
