#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import guizero
from datetime import datetime
import requests
import gpiozero
from mpu6050 import mpu6050
import board
from neopixel import NeoPixel
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




def make_test_gui():
    mpu = mpu6050(0x68)
    
    accel_closed = 5.0 #G's
    accel_open = 9.7 #G's

    
    direction_pin = 12 #GPIO 12 = rpi pin 32
    direction_device = gpiozero.DigitalOutputDevice(direction_pin)


    pwm_pin = 16 #GPIO 16 = rpi pin 36
    pwm_frequency_hz = 20_000
    pwm_duty_cycle_percent = 0;
    pwm_device = gpiozero.PWMOutputDevice(pwm_pin,  initial_value=pwm_duty_cycle_percent, frequency=pwm_frequency_hz)

    guizero_app = guizero.App(title="Motor tester")
    guizero.Text(guizero_app, text="Set duty cycle:")
    
    def handle_slider_change(new_value_str):
        pwm_device.value = int(new_value_str)/100
    guizero.Slider(guizero_app, command=handle_slider_change, start=0, end=100, width="fill")

    guizero_checkbox = None
    
    def handle_checkbox():
        direction_device.value = guizero_checkbox.value
    guizero_checkbox = guizero.CheckBox(guizero_app, text="Other direction", command=handle_checkbox)
    
    direction_device.value = guizero_checkbox.value
    
    
    #textAccel = guizero.Text(guizero_app, text="Z acceleration: ???")
    #def update_accelerometer():
    #    nonlocal latest_accel_z
    #    latest_accel_z = mpu.get_accel_data()["z"]
    #    textAccel.value = "Z acceleration: {:4.2f}".format(latest_accel_z)
    #guizero_app.repeat(100, update_accelerometer)
    
    
    box_calibration_open = guizero.Box(guizero_app)
    button_set_open = guizero.PushButton(box_calibration_open, text="Set open", align="left")
    text_open = guizero.Text(box_calibration_open, text=accel_open, align="left")
    def set_cal_open():
        nonlocal accel_open
        accel_open = latest_accel_z
        text_open.value = "{:4.2f}".format(accel_open)
    button_set_open.update_command(set_cal_open)


    box_calibration_closed = guizero.Box(guizero_app)
    button_set_closed = guizero.PushButton(box_calibration_closed, text="Set closed", align="left")
    text_closed = guizero.Text(box_calibration_closed, text=accel_closed, align="left")
    def set_cal_closed():
        nonlocal accel_closed
        accel_closed = latest_accel_z
        text_open.value = "{:4.2f}".format(accel_closed)
    button_set_closed.update_command(set_cal_closed)
    
    
    
    def go_to(accel_target):
        print("\ngoing to " + str(accel_target))
        accel_present = mpu.get_accel_data()["z"]
        print("   present = {:4.2f}".format(accel_present))
        difference = accel_target - accel_present
        print("difference = {:4.2f}".format(difference))
        close_enough = 0.05
        if(abs(difference) < close_enough):
            print("close enough, returning")
            pwm_device.value = 0
            return
        direction_device.value = 1 if difference>0 else 0
        
        #pwm_max = 1
        #accel_to_start_slowing_down_at = 1
        #line_slope = 1 / accel_to_start_slowing_down_at
        #new_pwm_value = min(pwm_max, line_slope * abs(difference))
        #print("  new pwm = {:4.2f}".format(new_pwm_value))
        #pwm_device.value = new_pwm_value
        pwm_device.value = 1
        guizero_app.after(100, go_to, [accel_target]);
            
        
        
    
    box_go_to = guizero.Box(guizero_app)
    def go_to_closed():
        go_to(accel_closed)
    def go_to_open():
        go_to(accel_open)
    guizero.PushButton(box_go_to, text="Go to open", align="left", command=go_to_open)
    guizero.PushButton(box_go_to, text="Go to closed", align="left", command=go_to_closed)

    guizero_app.display() #blocks until the window is closed
    pwm_device.off()


def make_clock_gui():
    led_count = 35

    neopixels = NeoPixel(board.D18, led_count)

    guizero_app = guizero.App(title="Neopixel tester")


    box_hour = guizero.Box(guizero_app, width="fill")
    guizero.Text(box_hour, text="Hour: ", align="left")


    close_blinds_hour = 6
    open_blinds_hour = 10

    close_blinds_led_index = round(led_count * close_blinds_hour / 12)
    open_blinds_led_index = round(led_count * open_blinds_hour / 12)

    brightness_max = 10

    use_smoothing = True
    run_clock = True


    def handle_time_slider():
        update_time(
            int(slider_hour.value),
            int(slider_minute.value),
            int(slider_second.value)
        )


    def update_time(hour, minute, second):
        second_ratio = second / 60
        minute_ratio = (minute + second_ratio) / 60
        hour_ratio = (hour + minute_ratio) / 12
        
        hour_led_index = round(led_count * hour_ratio)
        minute_led_index = round(led_count * minute_ratio)
        
        for i in range(0, led_count):
            
            if use_smoothing:
                led_ratio = i / led_count
                hour_distance = abs(led_ratio - hour_ratio)
                minute_distance = abs(led_ratio - minute_ratio)
                
                rise = brightness_max
                run = 1 / led_count
                slope = -rise / run
                
                red = max(0, slope * hour_distance + brightness_max)
                blue = max(0, slope * minute_distance + brightness_max)
                
                
                
            else:
                red = 30 if i==hour_led_index else 0
                blue = 30 if i==minute_led_index else 0
               
            green = 0 #5 if (i >= close_blinds_led_index and i <= open_blinds_led_index) else 0
          
            
            neopixels[i] = (red, green, blue)
        
        
    slider_hour = guizero.Slider(box_hour, command=handle_time_slider, start=0, end=12, width="fill", align="left") 
     

    box_minute = guizero.Box(guizero_app, width="fill")
    guizero.Text(box_minute, text="Minute: ", align="left")
    slider_minute = guizero.Slider(box_minute, command=handle_time_slider, start=0, end=59, width="fill", align="left")

    box_second = guizero.Box(guizero_app, width="fill")
    guizero.Text(box_second, text="Second: ", align="left")
    slider_second = guizero.Slider(box_second, command=handle_time_slider, start=0, end=59, width="fill", align="left")

    def handle_brightness_slider(new_slider_value_string):
        nonlocal brightness_max
        brightness_max = int(new_slider_value_string)
        tick()
    box_brightness = guizero.Box(guizero_app, width="fill")
    guizero.Text(box_brightness, text="Brightness: ", align="left")
    slider_brightness = guizero.Slider(box_brightness, command=handle_brightness_slider, start=1, end=255, width="fill", align="left")
    slider_brightness.value = brightness_max

    if run_clock:
        interval_ms = 1000 * 10
        def tick():
            now = datetime.now()
            hour = now.hour
            if hour > 11:
                # 12 PM becomes hour zero
                hour = hour - 12
            minute = now.minute
            second = now.second
            #print("hour={:d} minute={:d}".format(hour, minute))
            
            slider_hour.value = hour
            slider_minute.value = minute
            slider_second.value = second
            
            update_time(hour, minute, second)
        guizero_app.repeat(interval_ms, tick)
        tick()
    else:
        update_time(0, 0, 0)
     
    guizero_app.display() #blocks until the window is closed

if __name__ == '__main__':
    make_test_gui()
