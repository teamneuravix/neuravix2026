from setuptools import find_packages
from setuptools import setup

setup(
    name='map_msgs',
    version='2.6.0',
    packages=find_packages(
        include=('map_msgs', 'map_msgs.*')),
)
