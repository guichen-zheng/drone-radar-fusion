# generated from rosidl_generator_py/resource/_idl.py.em
# with input from interface:msg/DroneDetect.idl
# generated code does not contain a copyright notice


# Import statements for member types

import builtins  # noqa: E402, I100

import math  # noqa: E402, I100

import rosidl_parser.definition  # noqa: E402, I100


class Metaclass_DroneDetect(type):
    """Metaclass of message 'DroneDetect'."""

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
            module = import_type_support('interface')
        except ImportError:
            import logging
            import traceback
            logger = logging.getLogger(
                'interface.msg.DroneDetect')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__msg__drone_detect
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__msg__drone_detect
            cls._CONVERT_TO_PY = module.convert_to_py_msg__msg__drone_detect
            cls._TYPE_SUPPORT = module.type_support_msg__msg__drone_detect
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__msg__drone_detect

            from std_msgs.msg import Header
            if Header.__class__._TYPE_SUPPORT is None:
                Header.__class__.__import_type_support__()

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
        }


class DroneDetect(metaclass=Metaclass_DroneDetect):
    """Message class 'DroneDetect'."""

    __slots__ = [
        '_header',
        '_drone_id',
        '_x',
        '_y',
        '_z',
        '_vx',
        '_vy',
        '_vz',
        '_confidence',
        '_bbox_x',
        '_bbox_y',
        '_bbox_w',
        '_bbox_h',
        '_label',
        '_is_tracked',
        '_lat',
        '_lng',
    ]

    _fields_and_field_types = {
        'header': 'std_msgs/Header',
        'drone_id': 'uint32',
        'x': 'double',
        'y': 'double',
        'z': 'double',
        'vx': 'double',
        'vy': 'double',
        'vz': 'double',
        'confidence': 'double',
        'bbox_x': 'int32',
        'bbox_y': 'int32',
        'bbox_w': 'int32',
        'bbox_h': 'int32',
        'label': 'string',
        'is_tracked': 'boolean',
        'lat': 'double',
        'lng': 'double',
    }

    SLOT_TYPES = (
        rosidl_parser.definition.NamespacedType(['std_msgs', 'msg'], 'Header'),  # noqa: E501
        rosidl_parser.definition.BasicType('uint32'),  # noqa: E501
        rosidl_parser.definition.BasicType('double'),  # noqa: E501
        rosidl_parser.definition.BasicType('double'),  # noqa: E501
        rosidl_parser.definition.BasicType('double'),  # noqa: E501
        rosidl_parser.definition.BasicType('double'),  # noqa: E501
        rosidl_parser.definition.BasicType('double'),  # noqa: E501
        rosidl_parser.definition.BasicType('double'),  # noqa: E501
        rosidl_parser.definition.BasicType('double'),  # noqa: E501
        rosidl_parser.definition.BasicType('int32'),  # noqa: E501
        rosidl_parser.definition.BasicType('int32'),  # noqa: E501
        rosidl_parser.definition.BasicType('int32'),  # noqa: E501
        rosidl_parser.definition.BasicType('int32'),  # noqa: E501
        rosidl_parser.definition.UnboundedString(),  # noqa: E501
        rosidl_parser.definition.BasicType('boolean'),  # noqa: E501
        rosidl_parser.definition.BasicType('double'),  # noqa: E501
        rosidl_parser.definition.BasicType('double'),  # noqa: E501
    )

    def __init__(self, **kwargs):
        assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
            'Invalid arguments passed to constructor: %s' % \
            ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        from std_msgs.msg import Header
        self.header = kwargs.get('header', Header())
        self.drone_id = kwargs.get('drone_id', int())
        self.x = kwargs.get('x', float())
        self.y = kwargs.get('y', float())
        self.z = kwargs.get('z', float())
        self.vx = kwargs.get('vx', float())
        self.vy = kwargs.get('vy', float())
        self.vz = kwargs.get('vz', float())
        self.confidence = kwargs.get('confidence', float())
        self.bbox_x = kwargs.get('bbox_x', int())
        self.bbox_y = kwargs.get('bbox_y', int())
        self.bbox_w = kwargs.get('bbox_w', int())
        self.bbox_h = kwargs.get('bbox_h', int())
        self.label = kwargs.get('label', str())
        self.is_tracked = kwargs.get('is_tracked', bool())
        self.lat = kwargs.get('lat', float())
        self.lng = kwargs.get('lng', float())

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
        if self.header != other.header:
            return False
        if self.drone_id != other.drone_id:
            return False
        if self.x != other.x:
            return False
        if self.y != other.y:
            return False
        if self.z != other.z:
            return False
        if self.vx != other.vx:
            return False
        if self.vy != other.vy:
            return False
        if self.vz != other.vz:
            return False
        if self.confidence != other.confidence:
            return False
        if self.bbox_x != other.bbox_x:
            return False
        if self.bbox_y != other.bbox_y:
            return False
        if self.bbox_w != other.bbox_w:
            return False
        if self.bbox_h != other.bbox_h:
            return False
        if self.label != other.label:
            return False
        if self.is_tracked != other.is_tracked:
            return False
        if self.lat != other.lat:
            return False
        if self.lng != other.lng:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @builtins.property
    def header(self):
        """Message field 'header'."""
        return self._header

    @header.setter
    def header(self, value):
        if __debug__:
            from std_msgs.msg import Header
            assert \
                isinstance(value, Header), \
                "The 'header' field must be a sub message of type 'Header'"
        self._header = value

    @builtins.property
    def drone_id(self):
        """Message field 'drone_id'."""
        return self._drone_id

    @drone_id.setter
    def drone_id(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'drone_id' field must be of type 'int'"
            assert value >= 0 and value < 4294967296, \
                "The 'drone_id' field must be an unsigned integer in [0, 4294967295]"
        self._drone_id = value

    @builtins.property
    def x(self):
        """Message field 'x'."""
        return self._x

    @x.setter
    def x(self, value):
        if __debug__:
            assert \
                isinstance(value, float), \
                "The 'x' field must be of type 'float'"
            assert not (value < -1.7976931348623157e+308 or value > 1.7976931348623157e+308) or math.isinf(value), \
                "The 'x' field must be a double in [-1.7976931348623157e+308, 1.7976931348623157e+308]"
        self._x = value

    @builtins.property
    def y(self):
        """Message field 'y'."""
        return self._y

    @y.setter
    def y(self, value):
        if __debug__:
            assert \
                isinstance(value, float), \
                "The 'y' field must be of type 'float'"
            assert not (value < -1.7976931348623157e+308 or value > 1.7976931348623157e+308) or math.isinf(value), \
                "The 'y' field must be a double in [-1.7976931348623157e+308, 1.7976931348623157e+308]"
        self._y = value

    @builtins.property
    def z(self):
        """Message field 'z'."""
        return self._z

    @z.setter
    def z(self, value):
        if __debug__:
            assert \
                isinstance(value, float), \
                "The 'z' field must be of type 'float'"
            assert not (value < -1.7976931348623157e+308 or value > 1.7976931348623157e+308) or math.isinf(value), \
                "The 'z' field must be a double in [-1.7976931348623157e+308, 1.7976931348623157e+308]"
        self._z = value

    @builtins.property
    def vx(self):
        """Message field 'vx'."""
        return self._vx

    @vx.setter
    def vx(self, value):
        if __debug__:
            assert \
                isinstance(value, float), \
                "The 'vx' field must be of type 'float'"
            assert not (value < -1.7976931348623157e+308 or value > 1.7976931348623157e+308) or math.isinf(value), \
                "The 'vx' field must be a double in [-1.7976931348623157e+308, 1.7976931348623157e+308]"
        self._vx = value

    @builtins.property
    def vy(self):
        """Message field 'vy'."""
        return self._vy

    @vy.setter
    def vy(self, value):
        if __debug__:
            assert \
                isinstance(value, float), \
                "The 'vy' field must be of type 'float'"
            assert not (value < -1.7976931348623157e+308 or value > 1.7976931348623157e+308) or math.isinf(value), \
                "The 'vy' field must be a double in [-1.7976931348623157e+308, 1.7976931348623157e+308]"
        self._vy = value

    @builtins.property
    def vz(self):
        """Message field 'vz'."""
        return self._vz

    @vz.setter
    def vz(self, value):
        if __debug__:
            assert \
                isinstance(value, float), \
                "The 'vz' field must be of type 'float'"
            assert not (value < -1.7976931348623157e+308 or value > 1.7976931348623157e+308) or math.isinf(value), \
                "The 'vz' field must be a double in [-1.7976931348623157e+308, 1.7976931348623157e+308]"
        self._vz = value

    @builtins.property
    def confidence(self):
        """Message field 'confidence'."""
        return self._confidence

    @confidence.setter
    def confidence(self, value):
        if __debug__:
            assert \
                isinstance(value, float), \
                "The 'confidence' field must be of type 'float'"
            assert not (value < -1.7976931348623157e+308 or value > 1.7976931348623157e+308) or math.isinf(value), \
                "The 'confidence' field must be a double in [-1.7976931348623157e+308, 1.7976931348623157e+308]"
        self._confidence = value

    @builtins.property
    def bbox_x(self):
        """Message field 'bbox_x'."""
        return self._bbox_x

    @bbox_x.setter
    def bbox_x(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'bbox_x' field must be of type 'int'"
            assert value >= -2147483648 and value < 2147483648, \
                "The 'bbox_x' field must be an integer in [-2147483648, 2147483647]"
        self._bbox_x = value

    @builtins.property
    def bbox_y(self):
        """Message field 'bbox_y'."""
        return self._bbox_y

    @bbox_y.setter
    def bbox_y(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'bbox_y' field must be of type 'int'"
            assert value >= -2147483648 and value < 2147483648, \
                "The 'bbox_y' field must be an integer in [-2147483648, 2147483647]"
        self._bbox_y = value

    @builtins.property
    def bbox_w(self):
        """Message field 'bbox_w'."""
        return self._bbox_w

    @bbox_w.setter
    def bbox_w(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'bbox_w' field must be of type 'int'"
            assert value >= -2147483648 and value < 2147483648, \
                "The 'bbox_w' field must be an integer in [-2147483648, 2147483647]"
        self._bbox_w = value

    @builtins.property
    def bbox_h(self):
        """Message field 'bbox_h'."""
        return self._bbox_h

    @bbox_h.setter
    def bbox_h(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'bbox_h' field must be of type 'int'"
            assert value >= -2147483648 and value < 2147483648, \
                "The 'bbox_h' field must be an integer in [-2147483648, 2147483647]"
        self._bbox_h = value

    @builtins.property
    def label(self):
        """Message field 'label'."""
        return self._label

    @label.setter
    def label(self, value):
        if __debug__:
            assert \
                isinstance(value, str), \
                "The 'label' field must be of type 'str'"
        self._label = value

    @builtins.property
    def is_tracked(self):
        """Message field 'is_tracked'."""
        return self._is_tracked

    @is_tracked.setter
    def is_tracked(self, value):
        if __debug__:
            assert \
                isinstance(value, bool), \
                "The 'is_tracked' field must be of type 'bool'"
        self._is_tracked = value

    @builtins.property
    def lat(self):
        """Message field 'lat'."""
        return self._lat

    @lat.setter
    def lat(self, value):
        if __debug__:
            assert \
                isinstance(value, float), \
                "The 'lat' field must be of type 'float'"
            assert not (value < -1.7976931348623157e+308 or value > 1.7976931348623157e+308) or math.isinf(value), \
                "The 'lat' field must be a double in [-1.7976931348623157e+308, 1.7976931348623157e+308]"
        self._lat = value

    @builtins.property
    def lng(self):
        """Message field 'lng'."""
        return self._lng

    @lng.setter
    def lng(self, value):
        if __debug__:
            assert \
                isinstance(value, float), \
                "The 'lng' field must be of type 'float'"
            assert not (value < -1.7976931348623157e+308 or value > 1.7976931348623157e+308) or math.isinf(value), \
                "The 'lng' field must be a double in [-1.7976931348623157e+308, 1.7976931348623157e+308]"
        self._lng = value
