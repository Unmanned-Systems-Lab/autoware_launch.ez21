import os
import subprocess
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    
    # 执行 sudo chmod 命令，修改权限
    try:
        subprocess.run(['sudo', 'chmod', '666', '/dev/ttyACM0'], check=True, input='123\n', text=True)
        print(f"Success executing chmod")
    except subprocess.CalledProcessError as e:
        print(f"Error executing chmod")
    
    # 设置 imu 节点参数
    config = os.path.join(
        get_package_share_directory('tm_imu'),
        'config',
        'params.yaml'
    )

    imu_node = Node(
        package="tm_imu",
        executable="transducer_m_imu",
        name="tm_imu",
        output="screen",
        parameters=[config],
    )

    return LaunchDescription([imu_node])
