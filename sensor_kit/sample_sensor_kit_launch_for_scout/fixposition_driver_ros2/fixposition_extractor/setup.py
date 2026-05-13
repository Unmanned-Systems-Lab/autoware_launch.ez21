from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'fixposition_extractor'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # 安装 launch 文件夹中的所有 .launch.xml 文件
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.xml'))
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='lhl',
    maintainer_email='multimeters@live.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'pose_twist_extractor = fixposition_extractor.pose_twist_extractor:main',
            'imu_to_acc = fixposition_extractor.imu_to_acc:main', 
            'perception_sim = fixposition_extractor.perception_sim:main',
            'control_sim = fixposition_extractor.control_sim:main',
        ],
    },
)
