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
            'detect_lego = perception.detect_lego:main',
            'lego_vision_node = perception.lego_vision_node:main',  # ← ajouté
        ],
    },
)
