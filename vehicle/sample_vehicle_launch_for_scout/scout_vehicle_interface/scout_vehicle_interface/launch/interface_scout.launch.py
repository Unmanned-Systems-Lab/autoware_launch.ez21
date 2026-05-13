from launch import LaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    # 获取两个子launch文件的路径
    package_name1 = "scout_base"  # 替换为实际包名
    package_name2 = "scout_vehicle_interface"
    launch_file_1 = os.path.join(get_package_share_directory(package_name1), 'launch', 'scout_base.launch.py')
    launch_file_2 = os.path.join(get_package_share_directory(package_name2), 'launch', 'interface_v2.launch.py')

    # Include子launch文件
    included_launch_1 = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(launch_file_1)
    )

    included_launch_2 = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(launch_file_2)
    )

    # 创建LaunchDescription并包含两个子launch文件
    return LaunchDescription([
        included_launch_1,
        included_launch_2,
    ])
