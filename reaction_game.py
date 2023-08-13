import machine
import utime


# Configuration Constants
LED_JUMP_TIME = 0.05 # in seconds
TIME_DECREMENT = 0.05 # in seconds
DEBOUNCE_TIME = 150 # in ms

# Initialization
pins_out = [machine.Pin(i, machine.Pin.OUT) for i in range(6)]
full_sequence = pins_out + list(reversed(pins_out[1:-1]))
pin_button = machine.Pin(16, machine.Pin.IN)
button_pressed = False
last_interrupt_time = utime.ticks_add(utime.ticks_ms(), -DEBOUNCE_TIME)

def is_valid_press():
    """Check if the button press is valid (debounce)."""
    global last_interrupt_time
    current_time = utime.ticks_ms()
    if utime.ticks_diff(current_time, last_interrupt_time) < DEBOUNCE_TIME:
        return False
    last_interrupt_time = current_time
    return True

def button_isr(pin):
    """Interrupt service routine for the button."""
    global button_pressed
    if not button_pressed and is_valid_press():
        button_pressed = True


pin_button.irq(trigger=machine.Pin.IRQ_FALLING, handler=button_isr)


def initialize_round():
    """Reset game state for a new round."""
    global frozen_pins, target_pin, won_round
    frozen_pins = [False for _ in range(len(pins_out))]
    target_pin = 0
    won_round = False
    off_leds()
    
def off_leds():
    """Turn off all LEDs."""
    for pin in pins_out:
        pin.off()
    
def won_animation():
    """Display a winning animation using LEDs."""
    for pin in pins_out:
        pin.on()
    utime.sleep(1)
    global button_pressed
    button_pressed = False
    alternate = False
    while not button_pressed:
        for index, pin in enumerate(pins_out):
            if (index % 2 == 0) == alternate:
                pin.on()
            else:
                pin.off()
        alternate = not alternate
        utime.sleep(0.5)


def game_logic(index):
    """Implement game's core logic for button presses."""
    global button_pressed, won_round, target_pin, sleep_time
    if not button_pressed:
        return False
    
    if won_round:
        sleep_time -= TIME_DECREMENT
        initialize_round()
    elif target_pin == index:
        frozen_pins[index] = True
        target_pin += 1
        if target_pin >= len(pins_out) - 1:
            won_round = True
            if sleep_time - TIME_DECREMENT < TIME_DECREMENT:
                won_animation()
                machine.soft_reset()
    else:
        pass
        #button_pressed = False
        #while(not button_pressed):
        #    pass
        #machine.soft_reset()
        
    button_pressed = False
    return True


def main_game_loop():
    """Main game loop."""
    global sleep_time
    sleep_time = LED_JUMP_TIME
    initialize_round()
    while True:
        for index, pin in enumerate(full_sequence):
            if index >= len(pins_out):
                index = 2 * len(pins_out) - index - 2

            if not frozen_pins[index]:
                pin.on()
                utime.sleep(sleep_time)
                if (not game_logic(index)):
                    pin.off()

if __name__ == '__main__':
    main_game_loop()
