#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>

typedef struct {
    uint8_t pin;
    uint8_t level;
    uint32_t sequence;
} DeviceEvent;

int main(void) {
    const DeviceEvent event = {13U, 1U, 1U};

    printf("设备事件记录器 v0.1\n");
    printf("pin=%" PRIu8 ", level=%" PRIu8 ", sequence=%" PRIu32 "\n",
           event.pin, event.level, event.sequence);
    printf("event address=%p\n", (const void *)&event);
    return 0;
}
