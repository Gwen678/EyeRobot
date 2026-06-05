from setuptools import find_packages
from setuptools import setup

setup(
    name='nav_msgs',
    version='2.0.5',
    packages=find_packages(
        include=('nav_msgs', 'nav_msgs.*')),
)
