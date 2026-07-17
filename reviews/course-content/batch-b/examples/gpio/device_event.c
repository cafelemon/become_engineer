#include "device_event.h"

static DeviceEvent pending_event;
static bool has_pending_event = false;
static uint32_t next_sequence = 1U;

void simulator_reset(void) {
    pending_event = (DeviceEvent){0U, EDGE_FALLING, 0U};
    has_pending_event = false;
    next_sequence = 1U;
}

void gpio_edge_isr(uint8_t pin, Edge edge) {
    pending_event = (DeviceEvent){pin, edge, next_sequence};
    next_sequence += 1U;
    has_pending_event = true;
}

bool main_loop_take_event(DeviceEvent *event) {
    if (!has_pending_event || event == 0) {
        return false;
    }
    *event = pending_event;
    has_pending_event = false;
    return true;
}
