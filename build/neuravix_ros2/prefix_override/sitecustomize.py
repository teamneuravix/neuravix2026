import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/taha/Desktop/carla-ros2-ws/install/neuravix_ros2'
