# generated from rosidl_generator_py/resource/_idl.py.em
# with input from smart_can_msgs:msg/Fbmotordriver.idl
# generated code does not contain a copyright notice


# Import statements for member types

import builtins  # noqa: E402, I100

import rosidl_parser.definition  # noqa: E402, I100


class Metaclass_Fbmotordriver(type):
    """Metaclass of message 'Fbmotordriver'."""

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
                'smart_can_msgs.msg.Fbmotordriver')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__msg__fbmotordriver
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__msg__fbmotordriver
            cls._CONVERT_TO_PY = module.convert_to_py_msg__msg__fbmotordriver
            cls._TYPE_SUPPORT = module.type_support_msg__msg__fbmotordriver
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__msg__fbmotordriver

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
        }


class Fbmotordriver(metaclass=Metaclass_Fbmotordriver):
    """Message class 'Fbmotordriver'."""

    __slots__ = [
        '_gear_status_from_motor',
        '_plustripdistance',
        '_vehiclerpm',
    ]

    _fields_and_field_types = {
        'gear_status_from_motor': 'uint8',
        'plustripdistance': 'uint16',
        'vehiclerpm': 'uint16',
    }

    SLOT_TYPES = (
        rosidl_parser.definition.BasicType('uint8'),  # noqa: E501
        rosidl_parser.definition.BasicType('uint16'),  # noqa: E501
        rosidl_parser.definition.BasicType('uint16'),  # noqa: E501
    )

    def __init__(self, **kwargs):
        assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
            'Invalid arguments passed to constructor: %s' % \
            ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        self.gear_status_from_motor = kwargs.get('gear_status_from_motor', int())
        self.plustripdistance = kwargs.get('plustripdistance', int())
        self.vehiclerpm = kwargs.get('vehiclerpm', int())

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
        if self.gear_status_from_motor != other.gear_status_from_motor:
            return False
        if self.plustripdistance != other.plustripdistance:
            return False
        if self.vehiclerpm != other.vehiclerpm:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @builtins.property
    def gear_status_from_motor(self):
        """Message field 'gear_status_from_motor'."""
        return self._gear_status_from_motor

    @gear_status_from_motor.setter
    def gear_status_from_motor(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'gear_status_from_motor' field must be of type 'int'"
            assert value >= 0 and value < 256, \
                "The 'gear_status_from_motor' field must be an unsigned integer in [0, 255]"
        self._gear_status_from_motor = value

    @builtins.property
    def plustripdistance(self):
        """Message field 'plustripdistance'."""
        return self._plustripdistance

    @plustripdistance.setter
    def plustripdistance(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'plustripdistance' field must be of type 'int'"
            assert value >= 0 and value < 65536, \
                "The 'plustripdistance' field must be an unsigned integer in [0, 65535]"
        self._plustripdistance = value

    @builtins.property
    def vehiclerpm(self):
        """Message field 'vehiclerpm'."""
        return self._vehiclerpm

    @vehiclerpm.setter
    def vehiclerpm(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'vehiclerpm' field must be of type 'int'"
            assert value >= 0 and value < 65536, \
                "The 'vehiclerpm' field must be an unsigned integer in [0, 65535]"
        self._vehiclerpm = value
