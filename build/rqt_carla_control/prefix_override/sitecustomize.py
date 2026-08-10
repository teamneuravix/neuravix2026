import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/neuravix/Desktop/carla-ros2-ws/install/rqt_carla_control'
