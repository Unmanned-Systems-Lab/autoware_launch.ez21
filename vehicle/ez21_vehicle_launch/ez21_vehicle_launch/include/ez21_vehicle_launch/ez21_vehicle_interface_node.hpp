#ifndef EZ21_VEHICLE_LAUNCH__EZ21_VEHICLE_INTERFACE_NODE_HPP_
#define EZ21_VEHICLE_LAUNCH__EZ21_VEHICLE_INTERFACE_NODE_HPP_

#include <autoware_control_msgs/msg/control.hpp>
#include <autoware_vehicle_msgs/msg/gear_command.hpp>
#include <autoware_vehicle_msgs/msg/hazard_lights_command.hpp>
#include <autoware_vehicle_msgs/msg/turn_indicators_command.hpp>
#include <autoware_vehicle_msgs/srv/control_mode_command.hpp>
#include <rclcpp/rclcpp.hpp>
#include <tier4_vehicle_msgs/msg/actuation_command_stamped.hpp>

#include <optional>
#include <string>

namespace ez21_vehicle_launch
{

class Ez21VehicleInterfaceNode : public rclcpp::Node
{
public:
  explicit Ez21VehicleInterfaceNode(const rclcpp::NodeOptions & options = rclcpp::NodeOptions());

private:
  using Control = autoware_control_msgs::msg::Control;
  using GearCommand = autoware_vehicle_msgs::msg::GearCommand;
  using HazardLightsCommand = autoware_vehicle_msgs::msg::HazardLightsCommand;
  using TurnIndicatorsCommand = autoware_vehicle_msgs::msg::TurnIndicatorsCommand;
  using ControlModeCommand = autoware_vehicle_msgs::srv::ControlModeCommand;
  using ActuationCommandStamped = tier4_vehicle_msgs::msg::ActuationCommandStamped;

  void on_control_cmd(const Control::ConstSharedPtr msg);
  void on_actuation_cmd(const ActuationCommandStamped::ConstSharedPtr msg);
  void on_gear_cmd(const GearCommand::ConstSharedPtr msg);
  void on_turn_indicators_cmd(const TurnIndicatorsCommand::ConstSharedPtr msg);
  void on_hazard_lights_cmd(const HazardLightsCommand::ConstSharedPtr msg);
  void on_control_mode_request(
    const ControlModeCommand::Request::ConstSharedPtr request,
    const ControlModeCommand::Response::SharedPtr response);

  void handle_control_cmd(const Control & msg);
  void handle_actuation_cmd(const ActuationCommandStamped & msg);
  void handle_gear_cmd(const GearCommand & msg);
  void handle_turn_indicators_cmd(const TurnIndicatorsCommand & msg);
  void handle_hazard_lights_cmd(const HazardLightsCommand & msg);
  void handle_control_mode_request(
    const ControlModeCommand::Request & request,
    ControlModeCommand::Response & response);

  std::string vehicle_id_;
  bool use_actuation_command_;
  bool log_received_messages_;
  bool control_mode_request_default_success_;

  rclcpp::Subscription<Control>::SharedPtr sub_control_cmd_;
  rclcpp::Subscription<ActuationCommandStamped>::SharedPtr sub_actuation_cmd_;
  rclcpp::Subscription<GearCommand>::SharedPtr sub_gear_cmd_;
  rclcpp::Subscription<TurnIndicatorsCommand>::SharedPtr sub_turn_indicators_cmd_;
  rclcpp::Subscription<HazardLightsCommand>::SharedPtr sub_hazard_lights_cmd_;
  rclcpp::Service<ControlModeCommand>::SharedPtr srv_control_mode_request_;

  std::optional<Control> latest_control_cmd_;
  std::optional<ActuationCommandStamped> latest_actuation_cmd_;
  std::optional<GearCommand> latest_gear_cmd_;
  std::optional<TurnIndicatorsCommand> latest_turn_indicators_cmd_;
  std::optional<HazardLightsCommand> latest_hazard_lights_cmd_;
  std::optional<ControlModeCommand::Request> latest_control_mode_request_;
};

}  // namespace ez21_vehicle_launch

#endif  // EZ21_VEHICLE_LAUNCH__EZ21_VEHICLE_INTERFACE_NODE_HPP_
