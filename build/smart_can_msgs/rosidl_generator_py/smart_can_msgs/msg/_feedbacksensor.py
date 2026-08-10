# generated from rosidl_generator_py/resource/_idl.py.em
# with input from smart_can_msgs:msg/Feedbacksensor.idl
# generated code does not contain a copyright notice


# Import statements for member types

import builtins  # noqa: E402, I100

import rosidl_parser.definition  # noqa: E402, I100


class Metaclass_Feedbacksensor(type):
    """Metaclass of message 'Feedbacksensor'."""

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
                'smart_can_msgs.msg.Feedbacksensor')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__msg__feedbacksensor
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__msg__feedbacksensor
            cls._CONVERT_TO_PY = module.convert_to_py_msg__msg__feedbacksensor
            cls._TYPE_SUPPORT = module.type_support_msg__msg__feedbacksensor
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__msg__feedbacksensor

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
        }


class Feedbacksensor(metaclass=Metaclass_Feedbacksensor):
    """Message class 'Feedbacksensor'."""

    __slots__ = [
        '_steeringanglesensorhamdata',
        '_brakepedalsensorhamdata',
        '_handbrakesensor',
        '_handbrakesensor_hamdata',
        '_indir',
        '_kaldir',
        '_butonindir',
        '_butonkaldir',
    ]

    _fields_and_field_types = {
        'steeringanglesensorhamdata': 'uint8',
        'brakepedalsensorhamdata': 'uint8',
        'handbrakesensor': 'uint8',
        'handbrakesensor_hamdata': 'uint8',
        'indir': 'uint8',
        'kaldir': 'uint8',
        'butonindir': 'uint8',
        'butonkaldir': 'uint8',
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
    )

    def __init__(self, **kwargs):
        assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
            'Invalid arguments passed to constructor: %s' % \
            ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        self.steeringanglesensorhamdata = kwargs.get('steeringanglesensorhamdata', int())
        self.brakepedalsensorhamdata = kwargs.get('brakepedalsensorhamdata', int())
        self.handbrakesensor = kwargs.get('handbrakesensor', int())
        self.handbrakesensor_hamdata = kwargs.get('handbrakesensor_hamdata', int())
        self.indir = kwargs.get('indir', int())
        self.kaldir = kwargs.get('kaldir', int())
        self.butonindir = kwargs.get('butonindir', int())
        self.butonkaldir = kwargs.get('butonkaldir', int())

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
        if self.steeringanglesensorhamdata != other.steeringanglesensorhamdata:
            return False
        if self.brakepedalsensorhamdata != other.brakepedalsensorhamdata:
            return False
        if self.handbrakesensor != other.handbrakesensor:
            return False
        if self.handbrakesensor_hamdata != other.handbrakesensor_hamdata:
            return False
        if self.indir != other.indir:
            return False
        if self.kaldir != other.kaldir:
            return False
        if self.butonindir != other.butonindir:
            return False
        if self.butonkaldir != other.butonkaldir:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @builtins.property
    def steeringanglesensorhamdata(self):
        """Message field 'steeringanglesensorhamdata'."""
        return self._steeringanglesensorhamdata

    @steeringanglesensorhamdata.setter
    def steeringanglesensorhamdata(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'steeringanglesensorhamdata' field must be of type 'int'"
            assert value >= 0 and value < 256, \
                "The 'steeringanglesensorhamdata' field must be an unsigned integer in [0, 255]"
        self._steeringanglesensorhamdata = value

    @builtins.property
    def brakepedalsensorhamdata(self):
        """Message field 'brakepedalsensorhamdata'."""
        return self._brakepedalsensorhamdata

    @brakepedalsensorhamdata.setter
    def brakepedalsensorhamdata(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'brakepedalsensorhamdata' field must be of type 'int'"
            assert value >= 0 and value < 256, \
                "The 'brakepedalsensorhamdata' field must be an unsigned integer in [0, 255]"
        self._brakepedalsensorhamdata = value

    @builtins.property
    def handbrakesensor(self):
        """Message field 'handbrakesensor'."""
        return self._handbrakesensor

    @handbrakesensor.setter
    def handbrakesensor(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'handbrakesensor' field must be of type 'int'"
            assert value >= 0 and value < 256, \
                "The 'handbrakesensor' field must be an unsigned integer in [0, 255]"
        self._handbrakesensor = value

    @builtins.property
    def handbrakesensor_hamdata(self):
        """Message field 'handbrakesensor_hamdata'."""
        return self._handbrakesensor_hamdata

    @handbrakesensor_hamdata.setter
    def handbrakesensor_hamdata(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'handbrakesensor_hamdata' field must be of type 'int'"
            assert value >= 0 and value < 256, \
                "The 'handbrakesensor_hamdata' field must be an unsigned integer in [0, 255]"
        self._handbrakesensor_hamdata = value

    @builtins.property
    def indir(self):
        """Message field 'indir'."""
        return self._indir

    @indir.setter
    def indir(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'indir' field must be of type 'int'"
            assert value >= 0 and value < 256, \
                "The 'indir' field must be an unsigned integer in [0, 255]"
        self._indir = value

    @builtins.property
    def kaldir(self):
        """Message field 'kaldir'."""
        return self._kaldir

    @kaldir.setter
    def kaldir(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'kaldir' field must be of type 'int'"
            assert value >= 0 and value < 256, \
                "The 'kaldir' field must be an unsigned integer in [0, 255]"
        self._kaldir = value

    @builtins.property
    def butonindir(self):
        """Message field 'butonindir'."""
        return self._butonindir

    @butonindir.setter
    def butonindir(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'butonindir' field must be of type 'int'"
            assert value >= 0 and value < 256, \
                "The 'butonindir' field must be an unsigned integer in [0, 255]"
        self._butonindir = value

    @builtins.property
    def butonkaldir(self):
        """Message field 'butonkaldir'."""
        return self._butonkaldir

    @butonkaldir.setter
    def butonkaldir(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'butonkaldir' field must be of type 'int'"
            assert value >= 0 and value < 256, \
                "The 'butonkaldir' field must be an unsigned integer in [0, 255]"
        self._butonkaldir = value
