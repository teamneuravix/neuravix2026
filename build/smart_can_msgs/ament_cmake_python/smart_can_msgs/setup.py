from setuptools import find_packages
from setuptools import setup

setup(
    name='smart_can_msgs',
    version='0.0.0',
    packages=find_packages(
        include=('smart_can_msgs', 'smart_can_msgs.*')),
)
