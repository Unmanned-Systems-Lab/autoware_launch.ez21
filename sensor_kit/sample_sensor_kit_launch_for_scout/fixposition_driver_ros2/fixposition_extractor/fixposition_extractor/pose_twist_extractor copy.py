import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy
from fixposition_driver_ros2.msg import ODOMENU  # 引入消息类型
from geometry_msgs.msg import Pose, Twist, TransformStamped
from tf2_ros import TransformBroadcaster

class PoseTwistExtractor(Node):

    def __init__(self):
        super().__init__('pose_twist_extractor')

        # 设置 QoS Profile，并使用与发布端一致的 ReliabilityPolicy
        qos_profile = QoSProfile(depth=10)
        qos_profile.reliability = ReliabilityPolicy.BEST_EFFORT

        # 创建 Pose 和 Twist 发布者
        self.pose_pub = self.create_publisher(Pose, 'pose', qos_profile)
        self.twist_pub = self.create_publisher(Twist, 'twist', qos_profile)

        # 订阅 ODOMENU 消息
        self.subscription = self.create_subscription(
            ODOMENU,
            '/fixposition/fpa/odomenu',
            self.listener_callback,
            qos_profile
        )

        # 初始化 TF 广播器
        self.tf_broadcaster = TransformBroadcaster(self)

    def listener_callback(self, msg):
        # 提取 Pose 和 Twist
        pose_msg = msg.pose.pose  # 从 PoseWithCovariance 中提取 Pose
        twist_msg = msg.velocity.twist  # 从 TwistWithCovariance 中提取 Twist

        # 发布 Pose 和 Twist
        self.pose_pub.publish(pose_msg)
        self.twist_pub.publish(twist_msg)

        # 发布 TF (map -> base_link)
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

        #self.get_logger().info("Published Pose, Twist, and TF from map to base_link")

def main(args=None):
    rclpy.init(args=args)
    node = PoseTwistExtractor()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
