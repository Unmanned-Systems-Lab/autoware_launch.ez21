import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy
from fixposition_driver_ros2.msg import ODOMENU
from fixposition_driver_ros2.msg import LLH  # 引入 LLH 消息类型
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Pose, Twist, TransformStamped
from tf2_ros import TransformBroadcaster
from pyproj import Transformer


class OdometryPublisher(Node):
    def __init__(self):
        super().__init__('odometry_publisher')

        # 设置 QoS Profile
        qos_profile = QoSProfile(depth=1)
        qos_profile.reliability = ReliabilityPolicy.RELIABLE

        qos_profile_sub = QoSProfile(depth=1)
        qos_profile_sub.reliability = ReliabilityPolicy.BEST_EFFORT

        # 创建发布者
        self.pose_pub = self.create_publisher(Pose, 'pose', qos_profile)
        self.twist_pub = self.create_publisher(Twist, 'twist', qos_profile)
        self.odometry_pub = self.create_publisher(Odometry, 'localization/kinematic_state', qos_profile)

        # 初始化 TF 广播器
        self.tf_broadcaster = TransformBroadcaster(self)

        # 订阅 ODOMENU 消息
        self.subscription_odomenu = self.create_subscription(
            ODOMENU,
            '/fixposition/fpa/odomenu',
            self.listener_callback,
            qos_profile_sub
        )

        # 订阅 /fixposition/fpa/llh 消息
        self.subscription_llh = self.create_subscription(
            LLH,
            '/fixposition/fpa/llh',
            self.llh_callback,
            qos_profile_sub
        )

        # 初始化 UTM 转换器
        self.transformer = Transformer.from_crs("epsg:4326", "epsg:32649", always_xy=True)  # WGS84 转 UTM49N

        # 设置初始点经纬度
        initial_latitude = 29.571327391
        initial_longitude = 106.463983317

        # 将初始点经纬度转换为 UTM 坐标
        self.initial_utm_x, self.initial_utm_y = self.transformer.transform(initial_longitude, initial_latitude)

        # 初始化当前位置
        self.current_utm_x = None
        self.current_utm_y = None

        self.get_logger().info(f"Initial UTM Coordinates: x={self.initial_utm_x}, y={self.initial_utm_y}")

    def llh_callback(self, msg):
        """
        接收 LLH 消息，并转换为 UTM 坐标
        """
        lat = msg.position.x
        lon = msg.position.y

        # 经纬度 -> UTM 转换
        utm_x, utm_y = self.transformer.transform(lon, lat)  # 经度在前，纬度在后

        # 更新当前的 UTM 坐标
        self.current_utm_x = utm_x
        self.current_utm_y = utm_y

    def listener_callback(self, msg):
        """
        接收 ODOMENU 消息，并将 Pose 和 Twist 信息发布到对应话题
        """
        # 提取 Pose 和 Twist 信息
        pose_msg = msg.pose.pose  # 从 PoseWithCovariance 中提取 Pose
        twist_msg = msg.velocity.twist  # 从 TwistWithCovariance 中提取 Twist

        # 如果已经收到 LLH 数据，计算相对位置
        if self.current_utm_x is not None and self.current_utm_y is not None:
            relative_x = self.current_utm_x - self.initial_utm_x
            relative_y = self.current_utm_y - self.initial_utm_y

            # 更新 Pose 的位置
            pose_msg.position.x = relative_x
            pose_msg.position.y = relative_y

        # 发布 Pose 和 Twist
        self.pose_pub.publish(pose_msg)
        self.twist_pub.publish(twist_msg)

        # 创建新的 Odometry 消息
        odometry_msg = Odometry()
        odometry_msg.header = msg.header
        odometry_msg.header.frame_id = "map"
        odometry_msg.child_frame_id = 'base_link'
        odometry_msg.pose = msg.pose
        odometry_msg.twist = msg.velocity

        # 如果相对位置已计算，更新 Odometry 消息
        if self.current_utm_x is not None and self.current_utm_y is not None:
            odometry_msg.pose.pose.position.x = relative_x
            odometry_msg.pose.pose.position.y = relative_y

        # 发布 Odometry 消息
        self.odometry_pub.publish(odometry_msg)

        # 发布 TF (header.frame_id -> base_link)
        transform = TransformStamped()
        transform.header.stamp = self.get_clock().now().to_msg()
        transform.header.frame_id = 'map'
        transform.child_frame_id = 'base_link'

        # 设置位置和方向
        transform.transform.translation.x = pose_msg.position.x
        transform.transform.translation.y = pose_msg.position.y
        transform.transform.translation.z = pose_msg.position.z
        transform.transform.rotation = pose_msg.orientation

        # 发布 transform
        self.tf_broadcaster.sendTransform(transform)


def main(args=None):
    rclpy.init(args=args)
    node = OdometryPublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
