#include "ez21_vehicle_launch/ez21_vehicle_interface_node.hpp"

#include <algorithm>
#include <functional>
#include <utility>

namespace ez21_vehicle_launch
{

Ez21VehicleInterfaceNode::Ez21VehicleInterfaceNode(const rclcpp::NodeOptions & options)
: Node("ez21_vehicle_interface", options)
{
  vehicle_id_ = declare_parameter<std::string>("vehicle_id", "default");
  use_actuation_command_ = declare_parameter<bool>("use_actuation_command", false);
  log_received_messages_ = declare_parameter<bool>("log_received_messages", false);
  control_mode_request_default_success_ =
    declare_parameter<bool>("control_mode_request_default_success", true);

  auto qos_depth = declare_parameter<int64_t>("input_qos_depth", 1);
  qos_depth = std::max<int64_t>(1, qos_depth);
  auto qos = rclcpp::QoS(rclcpp::KeepLast(static_cast<size_t>(qos_depth)));

  using std::placeholders::_1;
  using std::placeholders::_2;

  sub_control_cmd_ = create_subscription<Control>(
    "input/control_cmd", qos, std::bind(&Ez21VehicleInterfaceNode::on_control_cmd, this, _1));

  if (use_actuation_command_) {
    sub_actuation_cmd_ = create_subscription<ActuationCommandStamped>(
      "input/actuation_cmd", qos, std::bind(&Ez21VehicleInterfaceNode::on_actuation_cmd, this, _1));
  }

  sub_gear_cmd_ = create_subscription<GearCommand>(
    "input/gear_cmd", qos, std::bind(&Ez21VehicleInterfaceNode::on_gear_cmd, this, _1));
  sub_turn_indicators_cmd_ = create_subscription<TurnIndicatorsCommand>(
    "input/turn_indicators_cmd", qos,
    std::bind(&Ez21VehicleInterfaceNode::on_turn_indicators_cmd, this, _1));
  sub_hazard_lights_cmd_ = create_subscription<HazardLightsCommand>(
    "input/hazard_lights_cmd", qos,
    std::bind(&Ez21VehicleInterfaceNode::on_hazard_lights_cmd, this, _1));
  srv_control_mode_request_ = create_service<ControlModeCommand>(
    "input/control_mode_request",
    std::bind(&Ez21VehicleInterfaceNode::on_control_mode_request, this, _1, _2));

  RCLCPP_INFO(
    get_logger(),
    "ez21_vehicle_interface started for vehicle_id='%s' (use_actuation_command=%s)",
    vehicle_id_.c_str(), use_actuation_command_ ? "true" : "false");
}
//请徐总填写这个函数
void Ez21VehicleInterfaceNode::on_control_cmd(const Control::ConstSharedPtr msg)
{
  latest_control_cmd_ = *msg;

  if (log_received_messages_) {
    RCLCPP_INFO_THROTTLE(
      get_logger(), *get_clock(), 2000,
      "Received control_cmd: velocity=%.3f acceleration=%.3f steering=%.3f",
      msg->longitudinal.velocity, msg->longitudinal.acceleration,
      msg->lateral.steering_tire_angle);
  }

  handle_control_cmd(*msg);
}

void Ez21VehicleInterfaceNode::on_actuation_cmd(const ActuationCommandStamped::ConstSharedPtr msg)
{
  latest_actuation_cmd_ = *msg;

  if (log_received_messages_) {
    RCLCPP_INFO_THROTTLE(
      get_logger(), *get_clock(), 2000,
      "Received actuation_cmd: accel=%.3f brake=%.3f steer=%.3f",
      msg->actuation.accel_cmd, msg->actuation.brake_cmd, msg->actuation.steer_cmd);
  }

  handle_actuation_cmd(*msg);
}
//请徐总填写这个函数
void Ez21VehicleInterfaceNode::on_gear_cmd(const GearCommand::ConstSharedPtr msg)
{
  latest_gear_cmd_ = *msg;

  if (log_received_messages_) {
    RCLCPP_INFO_THROTTLE(
      get_logger(), *get_clock(), 2000, "Received gear_cmd: command=%u",
      static_cast<unsigned int>(msg->command));
  }

  handle_gear_cmd(*msg);
}

void Ez21VehicleInterfaceNode::on_turn_indicators_cmd(
  const TurnIndicatorsCommand::ConstSharedPtr msg)
{
  latest_turn_indicators_cmd_ = *msg;

  if (log_received_messages_) {
    RCLCPP_INFO_THROTTLE(
      get_logger(), *get_clock(), 2000, "Received turn_indicators_cmd: command=%u",
      static_cast<unsigned int>(msg->command));
  }

  handle_turn_indicators_cmd(*msg);
}

void Ez21VehicleInterfaceNode::on_hazard_lights_cmd(const HazardLightsCommand::ConstSharedPtr msg)
{
  latest_hazard_lights_cmd_ = *msg;

  if (log_received_messages_) {
    RCLCPP_INFO_THROTTLE(
      get_logger(), *get_clock(), 2000, "Received hazard_lights_cmd: command=%u",
      static_cast<unsigned int>(msg->command));
  }

  handle_hazard_lights_cmd(*msg);
}

void Ez21VehicleInterfaceNode::on_control_mode_request(
  const ControlModeCommand::Request::ConstSharedPtr request,
  const ControlModeCommand::Response::SharedPtr response)
{
  latest_control_mode_request_ = *request;
  response->success = control_mode_request_default_success_;

  if (log_received_messages_) {
    RCLCPP_INFO(
      get_logger(), "Received control_mode_request: mode=%u",
      static_cast<unsigned int>(request->mode));
  }

  handle_control_mode_request(*request, *response);
}

void Ez21VehicleInterfaceNode::handle_control_cmd(const Control & /*msg*/)
{
  // TODO(ez21): Convert the latest Autoware control command into the target vehicle command.
}

void Ez21VehicleInterfaceNode::handle_actuation_cmd(const ActuationCommandStamped & /*msg*/)
{
  // TODO(ez21): Convert the latest raw actuation command into the target vehicle command.
}

void Ez21VehicleInterfaceNode::handle_gear_cmd(const GearCommand & /*msg*/)
{
  // TODO(ez21): Send the requested gear command to the target vehicle.
}

void Ez21VehicleInterfaceNode::handle_turn_indicators_cmd(
  const TurnIndicatorsCommand & /*msg*/)
{
  // TODO(ez21): Send the requested turn indicator command to the target vehicle.
}

void Ez21VehicleInterfaceNode::handle_hazard_lights_cmd(
  const HazardLightsCommand & /*msg*/)
{
  // TODO(ez21): Send the requested hazard lights command to the target vehicle.
}

void Ez21VehicleInterfaceNode::handle_control_mode_request(
  const ControlModeCommand::Request & /*request*/,
  ControlModeCommand::Response & /*response*/)
{
  // TODO(ez21): Replace the default service response with the actual mode transition result.
}

}  // namespace ez21_vehicle_launch
