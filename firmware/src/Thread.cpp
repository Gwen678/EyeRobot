#include "Thread.hpp"

#include "esp_log.h"

Thread::Thread(const char* name, uint32_t stack_size, UBaseType_t priority)
    : _name(name), _stack_size(stack_size), _priority(priority) {}

Thread::~Thread()
{
    if (_handle) {
        vTaskDelete(_handle);
        _handle = nullptr;
    }
}

void Thread::start()
{
    // A failed xTaskCreate must not pass silently; a task that
    // never spawns looks identical to a dead motor or dropped micro-ROS link.
    if (xTaskCreate(taskEntry, _name, _stack_size, this, _priority, &_handle) != pdPASS) {
        _handle = nullptr;
        ESP_LOGE("thread", "xTaskCreate failed for '%s' (stack=%u words): out of heap",
                 _name, (unsigned) _stack_size);
    }
}

void Thread::taskEntry(void* arg)
{
    static_cast<Thread*>(arg)->run();
    vTaskDelete(NULL);
}
