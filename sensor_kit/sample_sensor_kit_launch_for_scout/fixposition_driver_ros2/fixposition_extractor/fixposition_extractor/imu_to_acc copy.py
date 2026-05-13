import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu
from geometry_msgs.msg import AccelWithCovarianceStamped, AccelWithCovariance, Vector3
from std_msgs.msg import Header

class IMUToAccelerationNode(Node):
    def __init__(self):
        super().__init__('imu_to_acceleration_node')
        
        # 订阅 IMU 数据
        self.imu_subscription = self.create_subscription(
            Imu, 
            'imu_data',  # 这里使用你实际的IMU数据话题名称
            self.imu_callback, 
            10
        )
        
        # 发布 Acceleration 数据
        self.acceleration_publisher = self.create_publisher(
            AccelWithCovarianceStamped, 
            '/localization/acceleration', 
            10
        )
    
    def imu_callback(self, msg: Imu):
        # 创建 AccelWithCovarianceStamped 消息
        acceleration_msg = AccelWithCovarianceStamped()
        
        # 填充 Header
        acceleration_msg.header = Header()
        acceleration_msg.header.stamp = msg.header.stamp
        acceleration_msg.header.frame_id = 'base_link'  # 根据需要更改坐标系
        
        # 创建 AccelWithCovariance 消息并填充
        acceleration_msg.accel = AccelWithCovariance()

        # 提取线性加速度数据并填充 AccelWithCovariance 消息

        acceleration_msg.accel.accel.linear.x= msg.linear_acceleration.x
        acceleration_msg.accel.accel.linear.y = msg.linear_acceleration.y
        acceleration_msg.accel.accel.linear.z = msg.linear_acceleration.z
        
        # 提取角加速度数据并填充 AccelWithCovariance 消息
        acceleration_msg.accel.accel.angular.x = msg.angular_velocity.x
        acceleration_msg.accel.accel.angular.y = msg.angular_velocity.y
        acceleration_msg.accel.accel.angular.z = msg.angular_velocity.z
        
        # 设定协方差矩阵，这里假设为一个简单的零矩阵（需要根据实际数据进行调整）
        acceleration_msg.accel.covariance = [0.0] * 36
        
        # 发布加速度数据
        self.acceleration_publisher.publish(acceleration_msg)

def main(args=None):
    rclpy.init(args=args)
    node = IMUToAccelerationNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
