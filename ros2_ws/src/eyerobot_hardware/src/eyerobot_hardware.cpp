#include "eyerobot_hardware/eyerobot_hardware.hpp"

#include <cmath>
#include <stdexcept>

#include "pluginlib/class_list_macros.hpp"

namespace eyerobot_hardware {

// ── Lifecycle ───────────────────────────────────────────────────────────────

hardware_interface::CallbackReturn EyeRobotHardware::on_init(
  const hardware_interface::HardwareInfo & info)
{
  if (hardware_interface::SystemInterface::on_init(info) !=
      hardware_interface::CallbackReturn::SUCCESS)
  {
    return hardware_interface::CallbackReturn::ERROR;
  }

  // Parse hardware parameters from the URDF <ros2_control> block.
  auto get = [&](const std::string & key, const std::string & fallback) -> std::string {
    auto it = info_.hardware_parameters.find(key);
    return (it != info_.hardware_parameters.end()) ? it->second : fallback;
  };

  counts_per_rev_       = std::stod(get("counts_per_output_rev", "5756.0"));
  right_feedback_sign_  = std::stod(get("right_feedback_sign",   "1.0"));
  left_feedback_sign_   = std::stod(get("left_feedback_sign",    "-1.0"));
  right_fb_topic_       = get("right_fb_topic",  "motor_rwheel_fb");
  left_fb_topic_        = get("left_fb_topic",   "motor_lwheel_fb");
  right_cmd_topic_      = get("right_cmd_topic", "motor_rwheel_cmd");
  left_cmd_topic_       = get("left_cmd_topic",  "motor_lwheel_cmd");

  // Validate joints: expect exactly left_wheel_joint and right_wheel_joint.
  if (info_.joints.size() != 2) {
    RCLCPP_ERROR(rclcpp::get_logger("EyeRobotHardware"),
      "Expected 2 joints, got %zu", info_.joints.size());
    return hardware_interface::CallbackReturn::ERROR;
  }

  return hardware_interface::CallbackReturn::SUCCESS;
}

hardware_interface::CallbackReturn EyeRobotHardware::on_activate(
  const rclcpp_lifecycle::State & /*previous_state*/)
{
  // Reset state.
  right_position_ = left_position_ = 0.0;
  right_velocity_ = left_velocity_ = 0.0;
  right_command_  = left_command_  = 0.0;
  {
    std::lock_guard<std::mutex> lock(mutex_);
    right_count_ = left_count_ = std::numeric_limits<int32_t>::min();
    prev_right_  = prev_left_  = std::numeric_limits<int32_t>::min();
  }

  // Create a node for encoder subscriptions and command publishers.
  // Separate from controller_manager so QoS can match the micro-ROS firmware.
  node_ = std::make_shared<rclcpp::Node>("eyerobot_hardware");

  auto fb_qos  = rclcpp::QoS(1).best_effort();
  auto cmd_qos = rclcpp::QoS(1).reliable();

  right_fb_sub_ = node_->create_subscription<std_msgs::msg::Int32>(
    right_fb_topic_, fb_qos,
    [this](const std_msgs::msg::Int32::SharedPtr msg) {
      std::lock_guard<std::mutex> lock(mutex_);
      right_count_ = msg->data;
    });

  left_fb_sub_ = node_->create_subscription<std_msgs::msg::Int32>(
    left_fb_topic_, fb_qos,
    [this](const std_msgs::msg::Int32::SharedPtr msg) {
      std::lock_guard<std::mutex> lock(mutex_);
      left_count_ = msg->data;
    });

  right_cmd_pub_ = node_->create_publisher<std_msgs::msg::Float32>(right_cmd_topic_, cmd_qos);
  left_cmd_pub_  = node_->create_publisher<std_msgs::msg::Float32>(left_cmd_topic_,  cmd_qos);

  executor_ = std::make_shared<rclcpp::executors::SingleThreadedExecutor>();
  executor_->add_node(node_);
  spin_thread_ = std::thread([this]() { executor_->spin(); });

  RCLCPP_INFO(node_->get_logger(),
    "EyeRobot hardware activated — %.0f counts/rev, R sign=%.0f, L sign=%.0f",
    counts_per_rev_, right_feedback_sign_, left_feedback_sign_);

  return hardware_interface::CallbackReturn::SUCCESS;
}

hardware_interface::CallbackReturn EyeRobotHardware::on_deactivate(
  const rclcpp_lifecycle::State & /*previous_state*/)
{
  // Stop motors before shutting down.
  if (right_cmd_pub_ && left_cmd_pub_) {
    std_msgs::msg::Float32 zero;
    zero.data = 0.0f;
    right_cmd_pub_->publish(zero);
    left_cmd_pub_->publish(zero);
  }

  if (executor_) {
    executor_->cancel();
  }
  if (spin_thread_.joinable()) {
    spin_thread_.join();
  }

  right_fb_sub_.reset();
  left_fb_sub_.reset();
  right_cmd_pub_.reset();
  left_cmd_pub_.reset();
  executor_.reset();
  node_.reset();

  return hardware_interface::CallbackReturn::SUCCESS;
}

// ── State interfaces ────────────────────────────────────────────────────────

std::vector<hardware_interface::StateInterface>
EyeRobotHardware::export_state_interfaces()
{
  std::vector<hardware_interface::StateInterface> interfaces;
  for (const auto & joint : info_.joints) {
    if (joint.name == "right_wheel_joint") {
      interfaces.emplace_back(joint.name, hardware_interface::HW_IF_POSITION, &right_position_);
      interfaces.emplace_back(joint.name, hardware_interface::HW_IF_VELOCITY, &right_velocity_);
    } else if (joint.name == "left_wheel_joint") {
      interfaces.emplace_back(joint.name, hardware_interface::HW_IF_POSITION, &left_position_);
      interfaces.emplace_back(joint.name, hardware_interface::HW_IF_VELOCITY, &left_velocity_);
    }
  }
  return interfaces;
}

std::vector<hardware_interface::CommandInterface>
EyeRobotHardware::export_command_interfaces()
{
  std::vector<hardware_interface::CommandInterface> interfaces;
  for (const auto & joint : info_.joints) {
    if (joint.name == "right_wheel_joint") {
      interfaces.emplace_back(joint.name, hardware_interface::HW_IF_VELOCITY, &right_command_);
    } else if (joint.name == "left_wheel_joint") {
      interfaces.emplace_back(joint.name, hardware_interface::HW_IF_VELOCITY, &left_command_);
    }
  }
  return interfaces;
}

// ── Read (encoders → position / velocity) ───────────────────────────────────

hardware_interface::return_type EyeRobotHardware::read(
  const rclcpp::Time & /*time*/, const rclcpp::Duration & period)
{
  int32_t r_now, l_now;
  {
    std::lock_guard<std::mutex> lock(mutex_);
    r_now = right_count_;
    l_now = left_count_;
  }

  // Wait until first encoder messages arrive.
  const int32_t SENTINEL = std::numeric_limits<int32_t>::min();
  if (r_now == SENTINEL || l_now == SENTINEL) {
    return hardware_interface::return_type::OK;
  }

  // First valid pair: establish baseline without integrating.
  if (prev_right_ == SENTINEL || prev_left_ == SENTINEL) {
    prev_right_ = r_now;
    prev_left_  = l_now;
    return hardware_interface::return_type::OK;
  }

  double dt = period.seconds();
  if (dt <= 0.0) dt = 1.0 / 50.0;

  const double rad_per_count = 2.0 * M_PI / counts_per_rev_;
  // Same plausibility clamp as state_estimator_node: reject jumps > 5 revs.
  const double max_counts = 5.0 * counts_per_rev_;

  double delta_r = right_feedback_sign_ * static_cast<double>(r_now - prev_right_);
  double delta_l = left_feedback_sign_  * static_cast<double>(l_now - prev_left_);

  prev_right_ = r_now;
  prev_left_  = l_now;

  if (std::abs(delta_r) > max_counts || std::abs(delta_l) > max_counts) {
    // Implausible jump (e.g. firmware reboot resetting counter) — re-baseline,
    // no pose update. Mirrors state_estimator_node plausibility check.
    return hardware_interface::return_type::OK;
  }

  const double dr_rad = delta_r * rad_per_count;
  const double dl_rad = delta_l * rad_per_count;

  right_position_ += dr_rad;
  left_position_  += dl_rad;
  right_velocity_  = dr_rad / dt;
  left_velocity_   = dl_rad / dt;

  return hardware_interface::return_type::OK;
}

// ── Write (velocity commands → motor topics) ────────────────────────────────

hardware_interface::return_type EyeRobotHardware::write(
  const rclcpp::Time & /*time*/, const rclcpp::Duration & /*period*/)
{
  if (!right_cmd_pub_ || !left_cmd_pub_) {
    return hardware_interface::return_type::OK;
  }

  std_msgs::msg::Float32 r_msg, l_msg;
  r_msg.data = static_cast<float>(right_command_);
  l_msg.data = static_cast<float>(left_command_);
  right_cmd_pub_->publish(r_msg);
  left_cmd_pub_->publish(l_msg);

  return hardware_interface::return_type::OK;
}

}  // namespace eyerobot_hardware

PLUGINLIB_EXPORT_CLASS(
  eyerobot_hardware::EyeRobotHardware,
  hardware_interface::SystemInterface)
