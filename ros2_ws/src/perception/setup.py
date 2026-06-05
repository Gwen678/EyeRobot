from setuptools import find_packages, setup

package_name = 'perception'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # Deployed models (also runnable from the source tree).
        ('share/' + package_name + '/models', ['best.pt', 'best.blob']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='EyeRobot',
    maintainer_email='pcondesalvarelli@gmail.com',
    description='EyeRobot perception: Oak-D viewer, YOLO detection, RPLidar web viewer, dataset tools.',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            # The only real ROS 2 node. The others are standalone web/dev tools:
            #   python3 -m perception.oak_view      (Oak-D camera web viewer)
            #   python3 -m perception.lidar_web     (RPLidar web viewer)
            #   python3 -m perception.map_view      (map viewer)
            #   python3 -m perception.auto_label    (YOLO auto-labeler)
            #   python3 -m perception.check_labels  (label sanity check)
            'detect_lego = perception.detect_lego:main',
        ],
    },
)
