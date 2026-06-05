#pragma once

#include "freertos/FreeRTOS.h"
#include "freertos/queue.h"
#include <cstddef>

// Typed single-direction queue between two tasks.
// FreeRTOS pre-allocates storage for N items of sizeof(T) internally.
// Use this for small POD structs; for large payloads consider a pointer pool.
template<typename T, size_t N>
class Channel {
public:
    Channel() { _queue = xQueueCreate(N, sizeof(T)); }
    ~Channel() { vQueueDelete(_queue); }

    Channel(const Channel&) = delete;
    Channel& operator=(const Channel&) = delete;

    // Copy msg into the queue. Returns false if full.
    bool send(const T& msg, TickType_t timeout = 0)
    {
        return xQueueSend(_queue, &msg, timeout) == pdTRUE;
    }

    // Replace stale data with the newest value. This keeps stop commands from
    // being delayed behind older movement commands.
    bool sendLatest(const T& msg)
    {
        if (xQueueSend(_queue, &msg, 0) == pdTRUE) {
            return true;
        }

        T dropped;
        while (xQueueReceive(_queue, &dropped, 0) == pdTRUE) {}
        return xQueueSend(_queue, &msg, 0) == pdTRUE;
    }

    // Copy the oldest message out. Returns false on timeout.
    bool receive(T& msg, TickType_t timeout = portMAX_DELAY)
    {
        return xQueueReceive(_queue, &msg, timeout) == pdTRUE;
    }

    // Receive one message, then drain newer pending messages and return the
    // most recent one.
    bool receiveLatest(T& msg, TickType_t timeout = portMAX_DELAY)
    {
        if (xQueueReceive(_queue, &msg, timeout) != pdTRUE) {
            return false;
        }

        T newer;
        while (xQueueReceive(_queue, &newer, 0) == pdTRUE) {
            msg = newer;
        }
        return true;
    }

private:
    QueueHandle_t _queue;
};
