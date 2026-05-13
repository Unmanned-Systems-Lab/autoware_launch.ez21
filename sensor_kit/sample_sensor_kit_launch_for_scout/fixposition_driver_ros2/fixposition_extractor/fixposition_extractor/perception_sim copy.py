import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy
from autoware_auto_perception_msgs.msg import PredictedObjects
from nav_msgs.msg import OccupancyGrid
from autoware_perception_msgs.msg import TrafficSignalArray

class MultiTopicPublisher(Node):
    def __init__(self):
        super().__init__('multi_topic_publisher')

        # 创建 QoS 配置（设置为 reliable）
        qos_profile = QoSProfile(reliability=ReliabilityPolicy.RELIABLE, depth=10)

        # 创建发布器，使用 QoS 配置
        self.predicted_objects_publisher = self.create_publisher(
            PredictedObjects, '/perception/object_recognition/objects', qos_profile
        )
        self.occupancy_grid_publisher = self.create_publisher(
            OccupancyGrid, '/perception/occupancy_grid_map/map', qos_profile
        )
        self.traffic_signals_publisher = self.create_publisher(
            TrafficSignalArray, '/perception/traffic_light_recognition/traffic_signals', qos_profile
        )

        # 定时器分别发布三个消息
        self.timer = self.create_timer(1.0, self.publish_messages)
        self.get_logger().info("MultiTopicPublisher node has started with reliable QoS.")

    def publish_messages(self):
        self.publish_predicted_objects()
        self.publish_occupancy_grid()
        self.publish_traffic_signals()

    def publish_predicted_objects(self):
        # 创建 PredictedObjects 消息
        predicted_objects = PredictedObjects()
        predicted_objects.header.stamp = self.get_clock().now().to_msg()
        predicted_objects.header.frame_id = "map"
        predicted_objects.objects = []  # 确保 objects 字段为空

        # 发布 PredictedObjects 消息
        self.predicted_objects_publisher.publish(predicted_objects)
        self.get_logger().info("Published empty PredictedObjects message.")

    def publish_occupancy_grid(self):
        # 创建 OccupancyGrid 消息
        occupancy_grid = OccupancyGrid()

        # 设置 Header
        occupancy_grid.header.stamp = self.get_clock().now().to_msg()  # 使用当前时间
        occupancy_grid.header.frame_id = "map"

        # 设置地图信息
        occupancy_grid.info.map_load_time.sec = 0
        occupancy_grid.info.map_load_time.nanosec = 0
        occupancy_grid.info.resolution = 0.5
        occupancy_grid.info.width = 300
        occupancy_grid.info.height = 300
        occupancy_grid.info.origin.position.x = -74.5
        occupancy_grid.info.origin.position.y = -72.0
        occupancy_grid.info.origin.position.z = 0.0
        occupancy_grid.info.origin.orientation.x = 0.0
        occupancy_grid.info.origin.orientation.y = 0.0
        occupancy_grid.info.origin.orientation.z = 0.0
        occupancy_grid.info.origin.orientation.w = 1.0

        # 设置地图数据（填充为 1）
        occupancy_grid.data = [1] * (occupancy_grid.info.width * occupancy_grid.info.height)

        # 发布 OccupancyGrid 消息
        self.occupancy_grid_publisher.publish(occupancy_grid)
        self.get_logger().info("Published OccupancyGrid message with current timestamp.")

    def publish_traffic_signals(self):
        # 创建 TrafficSignalArray 消息
        traffic_signals = TrafficSignalArray()

        # 确保 signals 字段为空
        traffic_signals.signals = []

        # 发布 TrafficSignalArray 消息
        self.traffic_signals_publisher.publish(traffic_signals)
        self.get_logger().info("Published empty TrafficSignalArray message.")

def main(args=None):
    rclpy.init(args=args)
    node = MultiTopicPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
