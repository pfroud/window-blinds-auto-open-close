#!/usr/bin/env python3


import guizero
from datetime import datetime
import requests
from neopixel_ring_clock import NeopixelRingClock
from window_blinds import WindowBlinds
import traceback



def get_sunrise_time():
    # see https://sunrise-sunset.org/api
    url = "https://api.sunrise-sunset.org/json"
    params = {
            # Santa Clara, California (city not county)
            "lat": 37.354444,
            "lng": -121.969167,
            "formatted": 0
        }
    
    # When formatted==0, the response is ISO 8601 format.
    # The returned time is in UTC.
    
    try:
        response = requests.get(url, params=params).json()
    except requests.exceptions.RequestException as e:
        traceback.print_exc()
        return None
        
    
    if response["status"] == "OK":
        sunrise_string = response["results"]["sunrise"]
        return datetime.fromisoformat(sunrise_string).astimezone()
    else:
        print("sunrise-sunset.org API call failed, response status is ", response["status"])
        return None


def run_clock():
    def clock_tick():
        text.value = datetime.datetime.now().strftime("%I:%M:%S %p")        
    app.repeat(1000, clock_tick)




def make_motor_gui():
   
    pwm_pin = 16 #GPIO 16 = rpi pin 36
    direction_pin = 12 #GPIO 12 = rpi pin 32
    

    guizero_app = guizero.App(title="Motor tester")
    guizero.Text(guizero_app, text="Set duty cycle:")
    
    
    window_blinds = WindowBlinds(guizero_app, direction_pin, pwm_pin)
    
    def handle_slider_change(new_value_str):
        window_blinds.pwm_device.value = int(new_value_str)/100
    guizero.Slider(guizero_app, command=handle_slider_change, start=0, end=100, width="fill")

    guizero_checkbox = None
    
    def handle_checkbox():
        window_blinds.direction_device.value = guizero_checkbox.value
    guizero_checkbox = guizero.CheckBox(guizero_app, text="Other direction", command=handle_checkbox)
    
    window_blinds.direction_device.value = guizero_checkbox.value
    
    
    box_calibration_open = guizero.Box(guizero_app)
    button_set_open = guizero.PushButton(box_calibration_open, text="Set open", align="left")
    text_open = guizero.Text(box_calibration_open, text=window_blinds.accelerometer_Gs_open, align="left")
    def set_cal_open():
        text_open.value = "{:4.2f}".format(window_blinds.set_cal_open())
    button_set_open.update_command(set_cal_open)


    box_calibration_closed = guizero.Box(guizero_app)
    button_set_closed = guizero.PushButton(box_calibration_closed, text="Set closed", align="left")
    text_closed = guizero.Text(box_calibration_closed, text=window_blinds.accelerometer_Gs_closed, align="left")
    def set_cal_closed():
        text_closed.value = "{:4.2f}".format(window_blinds.set_cal_closed())
    button_set_closed.update_command(set_cal_closed)
        
    
    box_go_to = guizero.Box(guizero_app)
    def go_to_closed():
        window_blinds.go_to_closed()
    def go_to_open():
        window_blinds.go_to_open()
    guizero.PushButton(box_go_to, text="Go to open", align="left", command=go_to_open)
    guizero.PushButton(box_go_to, text="Go to closed", align="left", command=go_to_closed)

    guizero_app.display() #blocks until the guizero window is closed
    window_blinds.stop()
    


def make_clock_gui():
    
    guizero_app = guizero.App(title="Neopixel tester")
    
    pin = 18 #GPIO 18 = rpi pin 12
    led_count = 35
    brightness_max = 10
    use_smoothing = True
    clock = NeopixelRingClock(pin, led_count, brightness_max, use_smoothing)

    box_hour = guizero.Box(guizero_app, width="fill")
    guizero.Text(box_hour, text="Hour: ", align="left")


    #close_blinds_hour = 6
    #open_blinds_hour = 10
    #close_blinds_led_index = round(led_count * close_blinds_hour / 12)
    #open_blinds_led_index = round(led_count * open_blinds_hour / 12)

   
    run_clock = True


    def handle_time_slider():
        clock.update_time(
            int(slider_hour.value),
            int(slider_minute.value),
            int(slider_second.value)
        )
    slider_hour = guizero.Slider(box_hour, command=handle_time_slider, start=0, end=12, width="fill", align="left") 
     

    box_minute = guizero.Box(guizero_app, width="fill")
    guizero.Text(box_minute, text="Minute: ", align="left")
    slider_minute = guizero.Slider(box_minute, command=handle_time_slider, start=0, end=59, width="fill", align="left")

    box_second = guizero.Box(guizero_app, width="fill")
    guizero.Text(box_second, text="Second: ", align="left")
    slider_second = guizero.Slider(box_second, command=handle_time_slider, start=0, end=59, width="fill", align="left")

    def handle_brightness_slider(new_slider_value_string):
        clock.set_max_brightness(int(new_slider_value_string))
        
    box_brightness = guizero.Box(guizero_app, width="fill")
    guizero.Text(box_brightness, text="Brightness: ", align="left")
    slider_brightness = guizero.Slider(box_brightness, command=handle_brightness_slider, start=1, end=255, width="fill", align="left")
    slider_brightness.value = brightness_max

    
    interval_ms = 1000 * 10
    
    guizero_app.repeat(interval_ms, clock.tick)
    clock.tick()
    
     
    guizero_app.display() #blocks until the guizero window is closed

if __name__ == '__main__':
    make_motor_gui()
