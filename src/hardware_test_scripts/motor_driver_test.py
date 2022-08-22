import gpiozero
import os
import time
import guizero

# Test for L298 motor driver


def main():
    h_bridge_pin_1 = 13  # GPIO pin 13 == Raspberry Pi pin 33
    h_bridge_pin_2 = 6  # GPIO pin 6 == Raspberry Pi pin 31
    pwm_pin = 16  # GPIO pin 16 == Raspberry Pi pin 36

    gpio_device_H_bridge_pin_1 = gpiozero.DigitalOutputDevice(h_bridge_pin_1)
    gpio_device_H_bridge_pin_2 = gpiozero.DigitalOutputDevice(h_bridge_pin_2)
    gpio_device_motor_speed = gpiozero.PWMOutputDevice(
        pwm_pin, initial_value=0, frequency=1_000)

    guizero_app = guizero.App(title="Motor driver tester")

    guizero.Text(guizero_app, text="PWM frequency")

    def handle_pwm_frequency_changed():
        gpio_device_motor_speed.frequency = slider_pwm_frequency.value
    slider_pwm_frequency = guizero.Slider(guizero_app, start=1, end=gpio_device_motor_speed.frequency,
                                          command=handle_pwm_frequency_changed, width="fill")
    slider_pwm_frequency.value = gpio_device_motor_speed.frequency

    guizero.Box(guizero_app, height=50, width="fill")  # vertical spacer

    guizero.Text(guizero_app, text="PWM duty cycle")

    def handle_pwm_duty_cycle_changed():
        gpio_device_motor_speed.value = slider_pwm_duty_cycle.value / 100
    slider_pwm_duty_cycle = guizero.Slider(guizero_app, start=0, end=100,
                                           command=handle_pwm_duty_cycle_changed, width="fill")

    guizero.Box(guizero_app, height=50, width="fill")  # vertical spacer

    guizero.Text(guizero_app, text="Motor direction")

    def handle_direction_changed():
        selected_direction = buttongroup_direction.value
        if selected_direction == "Forward":
            gpio_device_H_bridge_pin_1.value = 1
            gpio_device_H_bridge_pin_2.value = 0
        elif selected_direction == "Reverse":
            gpio_device_H_bridge_pin_1.value = 0
            gpio_device_H_bridge_pin_2.value = 1
        elif selected_direction == "Off":
            gpio_device_H_bridge_pin_1.value = 0
            gpio_device_H_bridge_pin_2.value = 0
    buttongroup_direction = guizero.ButtonGroup(guizero_app,
                                                options=["Forward",
                                                         "Reverse", "Off"],
                                                command=handle_direction_changed)
    handle_direction_changed()  # set the H-bridge pins

    guizero_app.display()  # blocks until the guizero window is closed


if __name__ == '__main__':
    if os.geteuid() == 0:
        main()
    else:
        exit(__file__ + ": Need to run the script as root (use sudo) to access GPIO.")
