#pragma once

#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

// Abstract base class. Subclass and override run(), then call start().
// Call start() at the end of the derived constructor so the vtable is ready.
class Thread {
public:
    Thread(const char* name, uint32_t stack_size, UBaseType_t priority);
    virtual ~Thread();

    Thread(const Thread&) = delete;
    Thread& operator=(const Thread&) = delete;

    void start();
    TaskHandle_t handle() const { return _handle; }

protected:
    virtual void run() = 0;

private:
    static void taskEntry(void* arg);

    const char*   _name;
    uint32_t      _stack_size;
    UBaseType_t   _priority;
    TaskHandle_t  _handle = nullptr;
};
