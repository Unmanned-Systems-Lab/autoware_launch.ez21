from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='scout_vehicle_interface',
            executable='autoware_to_scout',
            name='autoware_to_scout'
        ),
        Node(
            package='scout_vehicle_interface',
            executable='scout_to_autoware',
            name='scout_to_autoware'
        ),
    ])
