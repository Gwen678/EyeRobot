#include "MicroRosTask.hpp"

#include <string.h>
#include <unistd.h>

#include <driver/uart.h>
#include <esp_log.h>
#include <esp_system.h>
#include <rcl/error_handling.h>
#include <rclc/rclc.h>
#include <rmw_microros/rmw_microros.h>
#include <rmw_microxrcedds_c/config.h>
#include <std_msgs/msg/float32.h>
#include <std_msgs/msg/int32.h>

#include "esp32_serial_transport.h"

#define RCL_CLEANUP(fn) do { if (fn) {} } while (0)

// Static member definitions
rcl_publisher_t            MicroRosTask::_publishers[MOTOR_COUNT];
std_msgs__msg__Int32       MicroRosTask::_pub_msgs[MOTOR_COUNT];

rcl_publisher_t            MicroRosTask::_speed_publishers[MOTOR_COUNT];
std_msgs__msg__Float32     MicroRosTask::_speed_msgs[MOTOR_COUNT];

rcl_subscription_t         MicroRosTask::_subscribers[MOTOR_COUNT];
std_msgs__msg__Float32     MicroRosTask::_sub_msgs[MOTOR_COUNT];

MicroRosTask::SubCtx       MicroRosTask::_sub_ctxs[MOTOR_COUNT];
AppBus*                    MicroRosTask::_bus_ptr = nullptr;

static size_t g_uart_port = UART_NUM_0;

MicroRosTask::MicroRosTask(AppBus& bus)
    : Thread("uros_task", 16000, 5), _bus(bus)
{
    _bus_ptr = &bus;
    start();
}

// Timer callback - publishes feedback only
void MicroRosTask::timerCallback(rcl_timer_t* timer, int64_t)
{
    if (timer == nullptr) return;

    for (size_t i = 0; i < MOTOR_COUNT; ++i) {
        MotorFeedback fb;
        if (_bus_ptr->from_motor[i].receiveLatest(fb, 0)) {
            // Publish raw accumulated encoder ticks (0 for fans/belt).
            _pub_msgs[i].data   = fb.ticks;
            // Measured speed in rad/s (0 for fans/belt).
            _speed_msgs[i].data = fb.speed_rads;
        }
        if (rcl_publish(&_publishers[i], &_pub_msgs[i], NULL)) {}
        if (rcl_publish(&_speed_publishers[i], &_speed_msgs[i], NULL)) {}
    }
}

// Subscription callback - forwards speed command to the motor task
void MicroRosTask::subscriptionCallback(const void* msg_in, void* ctx)
{
    const auto* msg = static_cast<const std_msgs__msg__Float32*>(msg_in);
    const auto* sc  = static_cast<const SubCtx*>(ctx);
    MotorCmd cmd;
    cmd.speed_rads = msg->data;
    _bus_ptr->to_motor[sc->idx].sendLatest(cmd);
}

// Entity setup
bool MicroRosTask::try_connect_and_setup(rclc_support_t&  support,
                                         rcl_node_t&      node,
                                         rcl_timer_t&     timer,
                                         rclc_executor_t& executor)
{
    rcl_allocator_t allocator = rcl_get_default_allocator();

    // Single attempt only; return false on failure so the caller re-pings before retrying.
    memset(&support, 0, sizeof(support));
    if (rclc_support_init(&support, 0, NULL, &allocator) != RCL_RET_OK) {
        return false;
    }

    uart_flush(UART_NUM_0);

    if (rclc_node_init_default(&node, "eyerobot_node", "", &support) != RCL_RET_OK) {
        rclc_support_fini(&support);
        return false;
    }

    // Publishers - one per motor (feedback). Unreliable QoS avoids ACK overhead on the shared UART.
    for (size_t i = 0; i < MOTOR_COUNT; ++i) {
        if (rclc_publisher_init_best_effort(
                &_publishers[i], &node,
                ROSIDL_GET_MSG_TYPE_SUPPORT(std_msgs, msg, Int32),
                kMotorConfigs[i].fb_topic) != RCL_RET_OK) {
            for (size_t j = 0; j < i; ++j)
                RCL_CLEANUP(rcl_publisher_fini(&_publishers[j], &node));
            RCL_CLEANUP(rcl_node_fini(&node));
            rclc_support_fini(&support);
            return false;
        }
        _pub_msgs[i].data = 0;
    }

    // Speed publishers - one per motor, measured speed in rad/s (Float32).
    // Only encoder wheels carry a real value; belt/fans publish 0.
    for (size_t i = 0; i < MOTOR_COUNT; ++i) {
        if (rclc_publisher_init_best_effort(
                &_speed_publishers[i], &node,
                ROSIDL_GET_MSG_TYPE_SUPPORT(std_msgs, msg, Float32),
                kMotorConfigs[i].speed_topic) != RCL_RET_OK) {
            for (size_t j = 0; j < i; ++j)
                RCL_CLEANUP(rcl_publisher_fini(&_speed_publishers[j], &node));
            for (size_t j = 0; j < MOTOR_COUNT; ++j)
                RCL_CLEANUP(rcl_publisher_fini(&_publishers[j], &node));
            RCL_CLEANUP(rcl_node_fini(&node));
            rclc_support_fini(&support);
            return false;
        }
        _speed_msgs[i].data = 0.0f;
    }

    // Subscribers - one per motor (command). Unreliable QoS matches the teleop publisher;
    // dropped samples are quickly superseded at 20 Hz.
    for (size_t i = 0; i < MOTOR_COUNT; ++i) {
        _sub_ctxs[i] = {i};
        if (rclc_subscription_init_best_effort(
                &_subscribers[i], &node,
                ROSIDL_GET_MSG_TYPE_SUPPORT(std_msgs, msg, Float32),
                kMotorConfigs[i].cmd_topic) != RCL_RET_OK) {
            for (size_t j = 0; j < i; ++j)
                RCL_CLEANUP(rcl_subscription_fini(&_subscribers[j], &node));
            for (size_t j = 0; j < MOTOR_COUNT; ++j) {
                RCL_CLEANUP(rcl_publisher_fini(&_speed_publishers[j], &node));
                RCL_CLEANUP(rcl_publisher_fini(&_publishers[j], &node));
            }
            RCL_CLEANUP(rcl_node_fini(&node));
            rclc_support_fini(&support);
            return false;
        }
    }

    if (rclc_timer_init_default(
            &timer, &support,
            RCL_MS_TO_NS(100), timerCallback) != RCL_RET_OK) {
        for (size_t i = 0; i < MOTOR_COUNT; ++i) {
            RCL_CLEANUP(rcl_subscription_fini(&_subscribers[i], &node));
            RCL_CLEANUP(rcl_publisher_fini(&_speed_publishers[i], &node));
            RCL_CLEANUP(rcl_publisher_fini(&_publishers[i], &node));
        }
        RCL_CLEANUP(rcl_node_fini(&node));
        rclc_support_fini(&support);
        return false;
    }

    // 1 timer + MOTOR_COUNT subscribers
    if (rclc_executor_init(&executor, &support.context,
                           1 + MOTOR_COUNT, &allocator) != RCL_RET_OK) {
        RCL_CLEANUP(rcl_timer_fini(&timer));
        for (size_t i = 0; i < MOTOR_COUNT; ++i) {
            RCL_CLEANUP(rcl_subscription_fini(&_subscribers[i], &node));
            RCL_CLEANUP(rcl_publisher_fini(&_speed_publishers[i], &node));
            RCL_CLEANUP(rcl_publisher_fini(&_publishers[i], &node));
        }
        RCL_CLEANUP(rcl_node_fini(&node));
        rclc_support_fini(&support);
        return false;
    }
    if (rclc_executor_add_timer(&executor, &timer) != RCL_RET_OK) {
        RCL_CLEANUP(rclc_executor_fini(&executor));
        RCL_CLEANUP(rcl_timer_fini(&timer));
        for (size_t i = 0; i < MOTOR_COUNT; ++i) {
            RCL_CLEANUP(rcl_subscription_fini(&_subscribers[i], &node));
            RCL_CLEANUP(rcl_publisher_fini(&_speed_publishers[i], &node));
            RCL_CLEANUP(rcl_publisher_fini(&_publishers[i], &node));
        }
        RCL_CLEANUP(rcl_node_fini(&node));
        rclc_support_fini(&support);
        return false;
    }

    for (size_t i = 0; i < MOTOR_COUNT; ++i) {
        if (rclc_executor_add_subscription_with_context(
                &executor, &_subscribers[i], &_sub_msgs[i],
                subscriptionCallback, &_sub_ctxs[i],
                ON_NEW_DATA) != RCL_RET_OK) {
            RCL_CLEANUP(rclc_executor_fini(&executor));
            RCL_CLEANUP(rcl_timer_fini(&timer));
            for (size_t j = 0; j < MOTOR_COUNT; ++j) {
                RCL_CLEANUP(rcl_subscription_fini(&_subscribers[j], &node));
                RCL_CLEANUP(rcl_publisher_fini(&_speed_publishers[j], &node));
                RCL_CLEANUP(rcl_publisher_fini(&_publishers[j], &node));
            }
            RCL_CLEANUP(rcl_node_fini(&node));
            rclc_support_fini(&support);
            return false;
        }
    }

    return true;
}

// Entity teardown
void MicroRosTask::destroy_entities(rclc_support_t&  support,
                                     rcl_node_t&      node,
                                     rcl_timer_t&     timer,
                                     rclc_executor_t& executor)
{
    RCL_CLEANUP(rclc_executor_fini(&executor));
    RCL_CLEANUP(rcl_timer_fini(&timer));
    for (size_t i = 0; i < MOTOR_COUNT; ++i) {
        RCL_CLEANUP(rcl_subscription_fini(&_subscribers[i], &node));
        RCL_CLEANUP(rcl_publisher_fini(&_speed_publishers[i], &node));
        RCL_CLEANUP(rcl_publisher_fini(&_publishers[i], &node));
    }
    RCL_CLEANUP(rcl_node_fini(&node));
    rclc_support_fini(&support);
}

// Task entry point
void MicroRosTask::run()
{
    rmw_uros_set_custom_transport(
        true,
        (void*) &g_uart_port,
        esp32_serial_open,
        esp32_serial_close,
        esp32_serial_write,
        esp32_serial_read);

    rclc_support_t  support;
    rcl_node_t      node;
    rcl_timer_t     timer;
    rclc_executor_t executor;

    bool connected = false;
    uint32_t spin_count = 0;
    uint32_t ping_failures = 0;

    // Motors stay gated to 0 until the first successful connection.
    _bus.link_up.store(false);

    while (true) {
        if (!connected) {
            // Wait until agent is reachable, then set up entities.
            if (rmw_uros_ping_agent(200, 1) != RMW_RET_OK) {
                vTaskDelay(pdMS_TO_TICKS(500));
                continue;
            }
            if (!try_connect_and_setup(support, node, timer, executor)) {
                vTaskDelay(pdMS_TO_TICKS(500));
                continue;
            }
            connected = true;
            spin_count = 0;
            ping_failures = 0;
            // Link is fully up: motors may now act on received commands.
            _bus.link_up.store(true);
        }

        rclc_executor_spin_some(&executor, RCL_MS_TO_NS(100));
        usleep(10000);

        // Check agent health every ~5 s to avoid interfering with UART data delivery.
        if (++spin_count >= 45) {
            spin_count = 0;

            ESP_LOGI("uros", "heap free=%u min=%u",
                     (unsigned) esp_get_free_heap_size(),
                     (unsigned) esp_get_minimum_free_heap_size());

            // Require two consecutive failures before acting; a single dropped reply is normal.
            if (rmw_uros_ping_agent(100, 3) != RMW_RET_OK) {
                if (++ping_failures >= 2) {
                    // Confirmed disconnect: gate motors to 0 and tear down entities.
                    _bus.link_up.store(false);
                    destroy_entities(support, node, timer, executor);
                    connected = false;
                    ping_failures = 0;
                }
            } else {
                ping_failures = 0;
            }
        }
    }
}
