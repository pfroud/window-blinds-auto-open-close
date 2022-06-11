import gpiozero
import os

def main():
    h_bridge_pin_1 =   # GPIO pin 13 == Raspberry Pi pin 33
    h_bridge_pin_2 = 6  # GPIO pin 6 == Raspberry Pi pin 31
    pwm_pin = 16  # GPIO pin 16 == Raspberry Pi pin 36
    
    gpio_device_H_bridge_pin_1 = gpiozero.DigitalOutputDevice(h_bridge_pin_1)
    gpio_device_H_bridge_pin_2 = gpiozero.DigitalOutputDevice(h_bridge_pin_2)
    gpio_device_motor_speed = gpiozero.PWMOutputDevice(pwm_pin, initial_value=0, frequency=20_000)
    
    gpio_device_H_bridge_pin_1.value = 1
    gpio_device_H_bridge_pin_2.value = 0
    gpio_device_motor_speed.value = 1
    
    
if __name__ == '__main__':
    if os.geteuid() == 0:
        main()
    else:
        exit(__file__ + ": Need to run the script as root (use sudo) to access GPIO.")
