#pragma once

#include <limits>
#include <memory>
#include <mutex>
#include <string>
#include <thread>

#include "hardware_interface/system_interface.hpp"
#include "hardware_interface/handle.hpp"
#include "hardware_interface/hardware_info.hpp"
#include "hardware_interface/types/hardware_interface_return_values.hpp"
#include "hardware_interface/types/hardware_interface_type_values.hpp"
#include "rclcpp/rclcpp.hpp"
#include "rclcpp_lifecycle/state.hpp"
#include "std_msgs/msg/float32.hpp"
#include "std_msgs/msg/int32.hpp"

namespace eyerobot_hardware {

class EyeRobotHardware : public hardware_interface::SystemInterface
{
public:
  RCLCPP_SHARED_PTR_DEFINITIONS(EyeRobotHardware)

  hardware_interface::CallbackReturn on_init(
    const hardware_interface::HardwareInfo & info) override;

  std::vector<hardware_interface::StateInterface> export_state_interfaces() override;
  std::vector<hardware_interface::CommandInterface> export_command_interfaces() override;

  hardware_interface::CallbackReturn on_activate(
    const rclcpp_lifecycle::State & previous_state) override;

  hardware_interface::CallbackReturn on_deactivate(
    const rclcpp_lifecycle::State & previous_state) override;

  hardware_interface::return_type read(
    const rclcpp::Time & time, const rclcpp::Duration & period) override;

  hardware_interface::return_type write(
    const rclcpp::Time & time, const rclcpp::Duration & period) override;

private:
  // Parameters (from URDF ros2_control block)
  double      counts_per_rev_{5756.0};
  double      right_feedback_sign_{1.0};
  double      left_feedback_sign_{-1.0};
  std::string right_fb_topic_{"motor_rwheel_fb"};
  std::string left_fb_topic_{"motor_lwheel_fb"};
  std::string right_cmd_topic_{"motor_rwheel_cmd"};
  std::string left_cmd_topic_{"motor_lwheel_cmd"};

  // State interfaces (position + velocity per wheel).
  // Positive = forward for both wheels (feedback_sign applied in read()).
  double right_position_{0.0};
  double left_position_{0.0};
  double right_velocity_{0.0};
  double left_velocity_{0.0};

  // Command interfaces
  double right_command_{0.0};
  double left_command_{0.0};

  // Encoder tracking
  // INT32_MIN is used as sentinel meaning "not yet received".
  std::mutex  mutex_;
  int32_t     right_count_{std::numeric_limits<int32_t>::min()};
  int32_t     left_count_{std::numeric_limits<int32_t>::min()};
  int32_t     prev_right_{std::numeric_limits<int32_t>::min()};
  int32_t     prev_left_{std::numeric_limits<int32_t>::min()};

  // ROS node for pub/sub (separate from controller_manager)
  rclcpp::Node::SharedPtr node_;
  rclcpp::Publisher<std_msgs::msg::Float32>::SharedPtr  right_cmd_pub_;
  rclcpp::Publisher<std_msgs::msg::Float32>::SharedPtr  left_cmd_pub_;
  rclcpp::Subscription<std_msgs::msg::Int32>::SharedPtr right_fb_sub_;
  rclcpp::Subscription<std_msgs::msg::Int32>::SharedPtr left_fb_sub_;
  std::shared_ptr<rclcpp::executors::SingleThreadedExecutor> executor_;
  std::thread spin_thread_;
};

}  // namespace eyerobot_hardware
