#include <tier4_vehicle_msgs/msg/battery_status.hpp>
#include <autoware_vehicle_msgs/msg/velocity_report.hpp>
#include <autoware_vehicle_msgs/msg/steering_report.hpp>
#include <scout_msgs/msg/scout_status.hpp>
#include <geometry_msgs/msg/twist_with_covariance_stamped.hpp>
#include <rclcpp/rclcpp.hpp>
#include <memory>
#include <iostream>
#include <cmath>
#include <chrono> // 包含 chrono 库

// float WHEEL_TREAD = 0.583;//scout的
float WHEEL_TREAD = 0.1;
float WHEEL_BASE = 0.498;

using namespace std::chrono_literals;

class Autoscoutsub : public rclcpp::Node
{
public:
    Autoscoutsub() : Node("Autoscoutsub"),count(0){
        RCLCPP_INFO(this->get_logger(),"SUB Node 启动");
        battery_status_pub_ = this->create_publisher<tier4_vehicle_msgs::msg::BatteryStatus>("/vehicle/status/battery_charge", rclcpp::QoS{1});//发布电池信息
        velocity_pub_ = this->create_publisher<autoware_vehicle_msgs::msg::VelocityReport>("/vehicle/status/velocity_status", rclcpp::QoS{1});//发布速度信息(线速度角速度)
        steerang_pub_ = this->create_publisher<autoware_vehicle_msgs::msg::SteeringReport>("/vehicle/status/steering_status", rclcpp::QoS{1});//发布角度信息
        vehicle_odom_pub_ = this->create_publisher<geometry_msgs::msg::TwistWithCovarianceStamped>("vehicle_velocity_converter/twist_with_covariance",rclcpp::QoS{1});//发布里程计信息

        // from vehicle to ros2 订阅底盘发给ros2的消息
        scout_status_sub_ = this->create_subscription<scout_msgs::msg::ScoutStatus>("/scout_status", 1, std::bind(&Autoscoutsub::callback_scout_status, this, std::placeholders::_1));//订阅底盘发来的信息
        timer_ = this->create_wall_timer(0.01s,std::bind(&Autoscoutsub::on_timer,this));//定时器
    };

private:
    // from vehicle 发布的车辆信息
    rclcpp::Publisher<tier4_vehicle_msgs::msg::BatteryStatus>::SharedPtr battery_status_pub_;//电池状况
    rclcpp::Publisher<autoware_vehicle_msgs::msg::VelocityReport>::SharedPtr velocity_pub_;//速度报告
    rclcpp::Publisher<autoware_vehicle_msgs::msg::SteeringReport>::SharedPtr steerang_pub_;//“转向角”报告
    rclcpp::Publisher<geometry_msgs::msg::TwistWithCovarianceStamped>::SharedPtr vehicle_odom_pub_;//里程计报告

    // from vehicle to ros 订阅来自底盘的消息
    rclcpp::Subscription<scout_msgs::msg::ScoutStatus>::SharedPtr scout_status_sub_;//小车底盘状况
    //定时器
    rclcpp::TimerBase::SharedPtr timer_;
    // 速度反馈
    double linear_velocity = 0.0;
    double angular_velocity = 0.0;
    
    //状态反馈
    int vehicle_state = 0;
    int control_mode = 0;
    int error_code = 0;
    double battery_voltage = 0.0;
    // int actuator_state = 0;

    //灯光反馈
    // bool light_ctrl_enabled = False;
    // int front_light_state = 0;
    // int rear_light_state = 0;

    //回调函数
    void callback_scout_status(const scout_msgs::msg::ScoutStatus::ConstSharedPtr msg)
    {
        // RCLCPP_INFO(this->get_logger(), "收到 scout_status");
        linear_velocity = msg->linear_velocity;
        angular_velocity = msg->angular_velocity;
        vehicle_state = msg->vehicle_state;
        control_mode = msg->control_mode;
        battery_voltage = msg->battery_voltage;
        error_code = msg->error_code;
        // actuator_state = msg.actuator_state;
        // light_ctrl_enabled = msg.light_ctrl_enabled;
        // front_light_state = msg.front_light_state;
        // rear_light_state = msg.rear_light_state;
    }

    void convert_battery_status_to_autoware_msg(tier4_vehicle_msgs::msg::BatteryStatus msg)//发布电池信息
    {
        msg.energy_level = battery_voltage;
        battery_status_pub_->publish(msg);
    }

    void convert_velocity_to_autoware_msg(autoware_vehicle_msgs::msg::VelocityReport msg)
    {   
        msg.longitudinal_velocity = linear_velocity;
        msg.lateral_velocity = angular_velocity;
        msg.header.frame_id = "base_link";//不明白为什么这里要设定为base_link
        velocity_pub_->publish(msg);
    }

    void convert_steerang_to_autoware_msg(autoware_vehicle_msgs::msg::SteeringReport msg)
    {
        msg.stamp = this->get_clock()->now();
        double v,w,angle;
        v = linear_velocity;
        w = angular_velocity;
        if(w==0||(abs(v)<0.01))
        {
            angle = 0;
        }
        else angle = atan2(WHEEL_TREAD * w,v);
        msg.steering_tire_angle = angle;
        steerang_pub_->publish(msg);
    }

    void send_odom_data_to_autoware(geometry_msgs::msg::TwistWithCovarianceStamped msg)
    {
        msg.header.frame_id = "base_link";
        msg.header.stamp = this->get_clock()->now();
        msg.twist.covariance = {0,0,0,0,0,0,
                                0,0,0,0,0,0,
                                0,0,0,0,0,0,
                                0,0,0,0,0,0,
                                0,0,0,0,0,0,
                                0,0,0,0,0,0};
        msg.twist.twist.linear.x = linear_velocity;
        msg.twist.twist.angular.z = angular_velocity;
        vehicle_odom_pub_->publish(msg);
    }

    size_t count;
    void on_timer(){
        // 给autoware的命令

        //发布电池状况
        tier4_vehicle_msgs::msg::BatteryStatus battery_status_msg;
        convert_battery_status_to_autoware_msg(battery_status_msg);

        //发布速度报告 将AKM转换为差速底盘需要的.以及角速度.这里报告的是车轮的转向角，实际上SCOUT只会发布角速度
        autoware_vehicle_msgs::msg::VelocityReport velocity_report_msg;
        convert_velocity_to_autoware_msg(velocity_report_msg);
        
        //发布转向角报告。控制器强制要求了这个部分
        autoware_vehicle_msgs::msg::SteeringReport steerang_report_msg;
        convert_steerang_to_autoware_msg(steerang_report_msg);

        //发布里程计信息
        geometry_msgs::msg::TwistWithCovarianceStamped vehicle_odom_msg;
        send_odom_data_to_autoware(vehicle_odom_msg);
  }

};

int main(int argc, char ** argv)
{
  //初始化客户端
  rclcpp::init(argc,argv);
  
  // 调用回旋函数
  rclcpp::spin(std::make_shared<Autoscoutsub>());
  // 释放资源
  rclcpp::shutdown();

  return 0;
}
