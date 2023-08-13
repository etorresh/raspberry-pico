import machine
import utime


# Config
# Time between led jumps
sleep_time = 0.15
# Debounce time between button presses
DEBOUNCE_TIME = 0.2
# Time to decrement from jumps after each round
TIME_DECREMENT = 0.05

pins_out = [machine.Pin(i, machine.Pin.OUT) for i in range(6)]

pin_button = machine.Pin(16, machine.Pin.IN)
last_interrupt_time = 0
button_pressed = False
def button_isr(pin):
    global button_pressed
    if button_pressed:
        return
        
    global last_interrupt_time
    current_time = utime.ticks_ms()
    
    if current_time - last_interrupt_time < DEBOUNCE_TIME:
        return
    
    last_interrupt_time = current_time
    
    button_pressed = True
    
pin_button.irq(trigger=machine.Pin.IRQ_FALLING, handler=button_isr)

full_sequence = pins_out + list(reversed(pins_out[1:-1]))
total_pins = len(pins_out)


def initialize_round_state():
    global frozen_pins, target_pin, won_round
    frozen_pins = [False for _ in range(len(pins_out))]
    target_pin = 0
    won_round = False
    off_leds()
    
def off_leds():
    for pin in pins_out:
        pin.off()
    
def won_animation():
    pass

initialize_round_state()
while True:
    for index, pin in enumerate(full_sequence):
        if index >= len(pins_out):
            index = 2*len(pins_out) - index - 2
        if not frozen_pins[index]:
            pin.on()
            utime.sleep(sleep_time)
            if button_pressed:
                if won_round:
                    sleep_time -= TIME_DECREMENT
                    if sleep_time < TIME_DECREMENT:
                        won_animation()
                    initialize_round_state()
                elif target_pin == index:
                    frozen_pins[index] = True
                    target_pin += 1
                    if target_pin >= len(pins_out) - 1:
                        won_round = True
                else:
                    # Soft reset doesn't work in debug mode in Thonny
                    machine.soft_reset()
                    
                button_pressed = False
            else:
                pin.off()
