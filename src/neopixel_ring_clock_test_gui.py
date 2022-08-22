
import os
import board
import guizero
from neopixel_ring_clock import NeopixelRingClock


def main():
    pin_neopixel = board.D21  # GPIO pin 21 == Raspberry Pi pin 40
    led_count = 35
    maximum_duty_cycle = 255
    neopixel_ring_clock = NeopixelRingClock(pin_neopixel, led_count,
                                            maximum_duty_cycle)

    guizero_app = guizero.App(title="Addressable LED ring clock tester")

    def update():
        hour = slider_hour.value
        minute = slider_minute.value
        second = slider_second.value
        text_selected_time.value = f"The selected time is {12 if hour==0 else hour}:{minute:02}:{second:02}"
        neopixel_ring_clock.override_time(hour, minute, second)
        neopixel_ring_clock.update()

    guizero.Text(guizero_app, text="Hour")
    slider_hour = guizero.Slider(guizero_app, start=0, end=11,
                                 command=update, width="fill")

    def handle_show_hour_changed():
        neopixel_ring_clock.set_show_hour(checkbox_show_hour.value == 1)
        neopixel_ring_clock.update()
    checkbox_show_hour = guizero.CheckBox(
        guizero_app, text="Show hour on ring clock")
    checkbox_show_hour.value = 1
    checkbox_show_hour.update_command(handle_show_hour_changed)

    guizero.Box(guizero_app, height=50, width="fill")  # vertical spacer

    guizero.Text(guizero_app, text="Minute")
    slider_minute = guizero.Slider(guizero_app, start=0, end=59,
                                   command=update, width="fill")

    def handle_show_minute_changed():
        neopixel_ring_clock.set_show_minute(checkbox_show_minute.value == 1)
        neopixel_ring_clock.update()
    checkbox_show_minute = guizero.CheckBox(
        guizero_app, text="Show minute on ring clock")
    checkbox_show_minute.value = 1
    checkbox_show_minute.update_command(handle_show_minute_changed)

    guizero.Box(guizero_app, height=50, width="fill")  # vertical spacer

    guizero.Text(guizero_app, text="Second")
    slider_second = guizero.Slider(guizero_app, start=0, end=59,
                                   command=update, width="fill")

    guizero.Box(guizero_app, height=50, width="fill")  # vertical spacer

    text_selected_time = guizero.Text(guizero_app)

    update()
    guizero_app.display()  # blocks until the guizero window is closed
    neopixel_ring_clock.all_off()


if __name__ == '__main__':
    if os.geteuid() == 0:
        main()
    else:
        exit(__file__ + ": Need to run the script as root (use sudo) to access GPIO.")
