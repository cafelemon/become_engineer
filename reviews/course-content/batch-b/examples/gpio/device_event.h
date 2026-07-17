#ifndef DEVICE_EVENT_H
#define DEVICE_EVENT_H

#include <stdbool.h>
#include <stdint.h>

typedef enum {
    EDGE_RISING,
    EDGE_FALLING
} Edge;

typedef struct {
    uint8_t pin;
    Edge edge;
    uint32_t sequence;
} DeviceEvent;

void simulator_reset(void);
void gpio_edge_isr(uint8_t pin, Edge edge);
bool main_loop_take_event(DeviceEvent *event);

#endif
