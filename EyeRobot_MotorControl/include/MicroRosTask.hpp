#pragma once

#include "AppBus.hpp"
#include "Thread.hpp"
#include <rcl/rcl.h>
#include <rclc/executor.h>
#include <rclc/rclc.h>
#include <std_msgs/msg/float32.h>
#include <std_msgs/msg/int32.h>

class MicroRosTask : public Thread {
public:
    explicit MicroRosTask(AppBus& bus);

protected:
    void run() override;

private:
    AppBus& _bus;

    // Static because rcl callbacks carry no user-data pointer (timer) or need
    // a stable address across reconnect cycles (subscription contexts).
    static rcl_publisher_t        _publishers[MOTOR_COUNT];
    static std_msgs__msg__Int32   _pub_msgs[MOTOR_COUNT];

    // Measured wheel speed (rad/s) telemetry — meaningful for the encoder
    // wheels, 0 for the encoder-less belt/fans. For verifying the encoder speed
    // estimate ahead of a closed-loop PI velocity controller.
    static rcl_publisher_t        _speed_publishers[MOTOR_COUNT];
    static std_msgs__msg__Float32 _speed_msgs[MOTOR_COUNT];

    static rcl_subscription_t     _subscribers[MOTOR_COUNT];
    static std_msgs__msg__Float32 _sub_msgs[MOTOR_COUNT];

    struct SubCtx { size_t idx; };
    static SubCtx  _sub_ctxs[MOTOR_COUNT];
    static AppBus* _bus_ptr;

    static void timerCallback(rcl_timer_t* timer, int64_t last_call_time);
    static void subscriptionCallback(const void* msg_in, void* ctx);

    bool try_connect_and_setup(rclc_support_t&  support,
                               rcl_node_t&      node,
                               rcl_timer_t&     timer,
                               rclc_executor_t& executor);

    void destroy_entities(rclc_support_t&  support,
                          rcl_node_t&      node,
                          rcl_timer_t&     timer,
                          rclc_executor_t& executor);
};
