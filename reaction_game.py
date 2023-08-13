import machine
import utime
import time


# Config
# Time between led jumps
sleep_time = 0.15
# Debounce time between button presses
debounce_time = 0.1

pins_out = [machine.Pin(i, machine.Pin.OUT) for i in range(6)]

pin_button = machine.Pin(16, machine.Pin.IN)
last_interrupt_time = 0
def button_isr(pin):
    global last_interrupt_time
    current_time = time.ticks_ms()
    
    if current_time - last_interrupt_time < debounce_time:
        return
    
    last_interrupt_time = current_time
    
    global button_pressed
    button_pressed = True
    
pin_button.irq(trigger=machine.Pin.IRQ_FALLING, handler=button_isr)
button_pressed = False

while True:
    for pin in (pins_out + list(reversed(pins_out[1:-1]))):
        if button_pressed:
            print("Button was pressed!")
            button_pressed = False
        pin.on()
        utime.sleep(sleep_time)
        pin.off()
