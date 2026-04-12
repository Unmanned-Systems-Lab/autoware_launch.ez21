import yaml

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.actions import OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import LoadComposableNodes
from launch_ros.descriptions import ComposableNode
from launch_ros.parameter_descriptions import ParameterValue


def get_vehicle_info(context):
    path = LaunchConfiguration("vehicle_param_file").perform(context)
    with open(path, "r") as f:
        params = yaml.safe_load(f)["/**"]["ros__parameters"]

    return {
        "min_longitudinal_offset": -params["rear_overhang"],
        "max_longitudinal_offset": params["front_overhang"] + params["wheel_base"],
        "min_lateral_offset": -(params["wheel_tread"] / 2.0 + params["right_overhang"]),
        "max_lateral_offset": params["wheel_tread"] / 2.0 + params["left_overhang"],
        "min_height_offset": 0.0,
        "max_height_offset": params["vehicle_height"],
    }


def launch_setup(context, *args, **kwargs):
    vehicle_info = get_vehicle_info(context)

    cuda_preprocessor_parameters = {
        "base_frame": ParameterValue(LaunchConfiguration("output_frame"), value_type=str),
        "use_imu": ParameterValue(LaunchConfiguration("use_imu"), value_type=bool),
        "use_3d_distortion_correction": ParameterValue(
            LaunchConfiguration("use_3d_distortion_correction"), value_type=bool
        ),
        "enable_ring_outlier_filter": ParameterValue(
            LaunchConfiguration("enable_ring_outlier_filter"), value_type=bool
        ),
        "distance_ratio": ParameterValue(
            LaunchConfiguration("distance_ratio"), value_type=float
        ),
        "object_length_threshold": ParameterValue(
            LaunchConfiguration("object_length_threshold"), value_type=float
        ),
        "processing_time_threshold_sec": ParameterValue(
            LaunchConfiguration("processing_time_threshold_sec"), value_type=float
        ),
        "timestamp_mismatch_fraction_threshold": ParameterValue(
            LaunchConfiguration("timestamp_mismatch_fraction_threshold"), value_type=float
        ),
        "crop_box.min_x": [vehicle_info["min_longitudinal_offset"]],
        "crop_box.max_x": [vehicle_info["max_longitudinal_offset"]],
        "crop_box.min_y": [vehicle_info["min_lateral_offset"]],
        "crop_box.max_y": [vehicle_info["max_lateral_offset"]],
        "crop_box.min_z": [vehicle_info["min_height_offset"]],
        "crop_box.max_z": [vehicle_info["max_height_offset"]],
        "crop_box.negative": [True],
    }

    nodes = [
        ComposableNode(
            package="autoware_cuda_pointcloud_preprocessor",
            plugin="autoware::cuda_pointcloud_preprocessor::CudaPointcloudPreprocessorNode",
            name="cuda_pointcloud_preprocessor",
            namespace="sensing/lidar/top/pointcloud_preprocessor",
            remappings=[
                ("~/input/pointcloud", LaunchConfiguration("input_pointcloud")),
                ("~/input/twist", LaunchConfiguration("input_twist")),
                ("~/input/imu", LaunchConfiguration("input_imu")),
                ("~/output/pointcloud", LaunchConfiguration("output_pointcloud")),
                ("~/output/pointcloud/cuda", [LaunchConfiguration("output_pointcloud"), "/cuda"]),
            ],
            parameters=[cuda_preprocessor_parameters],
            extra_arguments=[{"use_intra_process_comms": False}],
        ),
    ]

    return [
        LoadComposableNodes(
            composable_node_descriptions=nodes,
            target_container=LaunchConfiguration("pointcloud_container_name"),
        )
    ]


def generate_launch_description():
    return LaunchDescription(
        [
            DeclareLaunchArgument("pointcloud_container_name", default_value="pointcloud_container"),
            DeclareLaunchArgument("vehicle_param_file"),
            DeclareLaunchArgument("input_pointcloud_frame", default_value="m1_lidar"),
            DeclareLaunchArgument("input_frame", default_value="base_link"),
            DeclareLaunchArgument("output_frame", default_value="base_link"),
            DeclareLaunchArgument(
                "input_twist",
                default_value="/localization/twist_estimator/twist_with_covariance",
            ),
            DeclareLaunchArgument(
                "input_imu",
                default_value="/sensing/imu/imu_data",
            ),
            DeclareLaunchArgument(
                "input_pointcloud", default_value="/sensing/lidar/top/pointcloud_raw_ex"
            ),
            DeclareLaunchArgument(
                "output_pointcloud",
                default_value="/sensing/lidar/concatenated/pointcloud",
            ),
            DeclareLaunchArgument("use_imu", default_value="false"),
            DeclareLaunchArgument("use_3d_distortion_correction", default_value="false"),
            DeclareLaunchArgument("enable_ring_outlier_filter", default_value="false"),
            DeclareLaunchArgument("distance_ratio", default_value="1.03"),
            DeclareLaunchArgument("object_length_threshold", default_value="0.05"),
            DeclareLaunchArgument("processing_time_threshold_sec", default_value="0.01"),
            DeclareLaunchArgument(
                "timestamp_mismatch_fraction_threshold", default_value="0.01"
            ),
            DeclareLaunchArgument("use_intra_process", default_value="false"),
            OpaqueFunction(function=launch_setup),
        ]
    )

