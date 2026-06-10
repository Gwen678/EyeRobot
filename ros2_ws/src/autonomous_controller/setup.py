from setuptools import setup

package_name = 'autonomous_controller'

setup(
    name=package_name,
    version='0.1.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # Nav2 params used by the autonomous mission. manual_controller's
        # config/nav2_params.yaml is a relative symlink to this source file,
        # so keep its path stable.
        ('share/' + package_name + '/config', ['nav2_params_custom.yaml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Pedro Conde',
    maintainer_email='pcondesalvarelli@gmail.com',
    description='Mission behavior tree: flow-through Nav2 waypoint routes with pullback recovery.',
    license='MIT',
    entry_points={
        'console_scripts': [
            'behavior_tree = autonomous_controller.behavioral_tree:main',
        ],
    },
)
