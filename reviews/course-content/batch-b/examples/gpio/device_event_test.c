#include "device_event.h"

#include <assert.h>
#include <stdio.h>

int main(void) {
    DeviceEvent event;
    simulator_reset();
    assert(!main_loop_take_event(&event));

    gpio_edge_isr(13U, EDGE_RISING);
    assert(main_loop_take_event(&event));
    assert(event.pin == 13U);
    assert(event.edge == EDGE_RISING);
    assert(event.sequence == 1U);
    assert(!main_loop_take_event(&event));

    gpio_edge_isr(13U, EDGE_FALLING);
    assert(main_loop_take_event(&event));
    assert(event.edge == EDGE_FALLING);
    assert(event.sequence == 2U);

    simulator_reset();
    gpio_edge_isr(3U, EDGE_RISING);
    gpio_edge_isr(4U, EDGE_FALLING);
    assert(main_loop_take_event(&event));
    assert(event.pin == 4U);
    assert(event.edge == EDGE_FALLING);
    assert(event.sequence == 2U);

    puts("device event tests passed");
    return 0;
}
