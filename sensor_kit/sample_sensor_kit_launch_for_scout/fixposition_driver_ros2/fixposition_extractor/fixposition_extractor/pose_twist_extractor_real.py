import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy
from fixposition_driver_ros2.msg import ODOMENU  # 引入 ODOMENU 消息类型
from nav_msgs.msg import Odometry  # 引入 Odometry 消息类型
from geometry_msgs.msg import Pose, Twist, TransformStamped
from tf2_ros import TransformBroadcaster

class OdometryPublisher(Node):

    def __init__(self):
        super().__init__('odometry_publisher')

        # 设置 QoS Profile，并使用与发布端一致的 ReliabilityPolicy
        qos_profile = QoSProfile(depth=1)
        qos_profile.reliability = ReliabilityPolicy.RELIABLE

        # 设置 QoS Profile，并使用与发布端一致的 ReliabilityPolicy
        qos_profile_sub = QoSProfile(depth=1)
        qos_profile_sub.reliability = ReliabilityPolicy.BEST_EFFORT

        # 创建 Pose, Twist 和 Odometry 发布者
        self.pose_pub = self.create_publisher(Pose, 'pose', qos_profile)
        self.twist_pub = self.create_publisher(Twist, 'twist', qos_profile)
        self.odometry_pub = self.create_publisher(Odometry, 'localization/kinematic_state', qos_profile)

        # 订阅 ODOMENU 消息
        self.subscription_odomenu = self.create_subscription(
            ODOMENU,
            '/fixposition/fpa/odomenu',
            self.listener_callback,
            qos_profile_sub
        )

        # 初始化 TF 广播器
        self.tf_broadcaster = TransformBroadcaster(self)

    def listener_callback(self, msg):
        # 提取 Pose 和 Twist 信息
        pose_msg = msg.pose.pose  # 从 PoseWithCovariance 中提取 Pose
        twist_msg = msg.velocity.twist  # 从 TwistWithCovariance 中提取 Twist

        # 发布 Pose 和 Twist
        self.pose_pub.publish(pose_msg)
        self.twist_pub.publish(twist_msg)

        # 创建新的 Odometry 消息
        odometry_msg = Odometry()
        odometry_msg.header = msg.header
        odometry_msg.header.frame_id="map"
        odometry_msg.child_frame_id = 'base_link'
        odometry_msg.pose = msg.pose  # 假设 ODOMENU 中的 pose 已包含 covariance 信息
        odometry_msg.twist = msg.velocity  # 假设 ODOMENU 中的 velocity 已包含 covariance 信息

        # 发布组合后的 Odometry 消息
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

        # 输出日志信息
        #self.get_logger().info("Published Pose, Twist, Odometry, and TF from map to base_link")

def main(args=None):
    rclpy.init(args=args)
    node = OdometryPublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
