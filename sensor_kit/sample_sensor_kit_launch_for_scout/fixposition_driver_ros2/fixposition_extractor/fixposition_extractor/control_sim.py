import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy
from autoware_auto_vehicle_msgs.msg import SteeringReport

class SteeringStatusPublisher(Node):
    def __init__(self):
        super().__init__('steering_status_publisher')

        # 创建 QoS 配置（设置为 reliable）
        qos_profile = QoSProfile(reliability=ReliabilityPolicy.RELIABLE, depth=10)

        # 创建发布器，使用 QoS 配置
        self.publisher = self.create_publisher(SteeringReport, '/vehicle/status/steering_status', qos_profile)

        # 定时器发布消息
        self.timer = self.create_timer(0.1, self.publish_steering_status)
        #self.get_logger().info("SteeringStatusPublisher node has started with reliable QoS.")

    def publish_steering_status(self):
        # 创建 SteeringReport 消息
        steering_status = SteeringReport()

        # 设置消息内容
        steering_status.stamp = self.get_clock().now().to_msg()  # 当前时间
        steering_status.steering_tire_angle = 0.0  # 假设当前方向盘转角为 0

        # 发布消息
        self.publisher.publish(steering_status)
        #self.get_logger().info("Published SteeringReport message: "
        #                       f"stamp: {steering_status.stamp.sec}.{steering_status.stamp.nanosec}, "
        #                       f"steering_tire_angle: {steering_status.steering_tire_angle}")

def main(args=None):
    rclpy.init(args=args)
    node = SteeringStatusPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
