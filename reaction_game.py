import machine
import utime


# Config
# Time between led jumps in seconds
LED_JUMP_TIME = 0.15
# Debounce time between button presses in miliseconds
DEBOUNCE_TIME = 100
# Time to decrement from jumps after each round
TIME_DECREMENT = 0.05

pins_out = [machine.Pin(i, machine.Pin.OUT) for i in range(6)]

pin_button = machine.Pin(16, machine.Pin.IN)
button_pressed = False

last_interrupt_time = utime.ticks_add(utime.ticks_ms(), -DEBOUNCE_TIME)
def is_valid_press():
    global last_interrupt_time
    
    current_time = utime.ticks_ms()
    if utime.ticks_diff(current_time, last_interrupt_time) < DEBOUNCE_TIME:
        return False
    last_interrupt_time = current_time
    return True

def button_isr(pin):
    global button_pressed
    
    if button_pressed:
        return
    
    if is_valid_press():
        button_pressed = True

    
pin_button.irq(trigger=machine.Pin.IRQ_FALLING, handler=button_isr)

full_sequence = pins_out + list(reversed(pins_out[1:-1]))
total_pins = len(pins_out)


def initialize_round_state():
    global frozen_pins, target_pin, won_round, sleep_time
    frozen_pins = [False for _ in range(len(pins_out))]
    target_pin = 0
    won_round = False
    off_leds()
    
def off_leds():
    for pin in pins_out:
        pin.off()
    
def won_animation():
    pass

def get_actual_index(enumerated_index):
    if enumerated_index >= len(pins_out):
        return 2*len(pins_out) - enumerated_index - 2
    return enumerated_index

initialize_round_state()
sleep_time = LED_JUMP_TIME
while True:
    for index, pin in enumerate(full_sequence):
        index = get_actual_index(index)
        if not frozen_pins[index]:
            pin.on()
            utime.sleep(sleep_time)
            if button_pressed:
                if won_round:
                    sleep_time -= TIME_DECREMENT
                    if sleep_time < TIME_DECREMENT:
                        won_animation()
                        # Reset jump time
                        sleep_time = LED_JUMP_TIME
                        button_pressed = False
                        initialize_round_state()
                        break
                    initialize_round_state()
                elif target_pin == index:
                    frozen_pins[index] = True
                    target_pin += 1
                    if target_pin >= len(pins_out) - 1:
                        won_round = True
                else:
                    # Soft reset doesn't work in debug mode in Thonny
                    #machine.soft_reset()
                    pass
                    
                button_pressed = False
            else:
                pin.off()
