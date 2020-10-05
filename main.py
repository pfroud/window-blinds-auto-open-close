#!/usr/bin/env python3


import guizero
from datetime import datetime
import requests
from neopixel_ring_clock import NeopixelRingClock
from window_blinds import WindowBlinds
import traceback
import dateparser



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
        
         #formatString = "%I:%M:%S %p"
        #print("sunrise: ", datetime.fromisoformat(sunriseStr)
         #                     .astimezone()
          #                    .strftime(formatString)
           #               )
        
    
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


def make_end_user_gui():
    guizero_app = guizero.App(title="Window blinds thing")
    
    pwm_pin = 16 #GPIO 16 = rpi pin 36
    direction_pin = 12 #GPIO 12 = rpi pin 32
    window_blinds = WindowBlinds(guizero_app, direction_pin, pwm_pin)
     
    guizero.Box(guizero_app, height="10")
    
    #################### daily alarm ################
    box_daily_alarm = guizero.Box(guizero_app)
    box_daily_alarm.set_border(1, "#aaaaaa")
     
    guizero.Text(box_daily_alarm, text="Daily alarm")
    guizero.Box(box_daily_alarm, height="10")
    
    box_close_blinds_time = guizero.Box(box_daily_alarm)
    guizero.Text(box_close_blinds_time, text="Close blinds ", align="left")
    guizero.TextBox(box_close_blinds_time, align="left", text="60")
    guizero.Text(box_close_blinds_time, text="minutes before sunrise.", align="left")
    
    box_open_blinds_time = guizero.Box(box_daily_alarm)
    guizero.Text(box_open_blinds_time, text="Open blinds at ", align="left")
    guizero.TextBox(box_open_blinds_time, text="11 am", align="left")
    guizero.Text(box_open_blinds_time, text=".", align="left")
    
    guizero.PushButton(box_daily_alarm, text="Update")
    
    guizero.Box(guizero_app, height="20")
    
    ################## one-time custom alarm ##############
    box_custom_alarm = guizero.Box(guizero_app)
    box_custom_alarm.set_border(1, "#aaaaaa")
    guizero.Text(box_custom_alarm, text="Custom alarm")
    guizero.Box(box_custom_alarm, height="10")
    
    box_custom_alarm_time = guizero.Box(box_custom_alarm)
    guizero.Text(box_custom_alarm_time, text="Close blinds now, then open blinds ", align="left")
    textbox_custom_alarm = guizero.TextBox(box_custom_alarm_time, text="in 20 seconds", align="left")
    guizero.Text(box_custom_alarm_time, text=".", align="left")
    
    text_alarm_status = guizero.Text(box_custom_alarm, text="Press the button to set alarm")
    
    def update_custom_alarm():
        alarm_time_str = textbox_custom_alarm.value
        parsed_alarm_datetime = dateparser.parse(alarm_time_str)
        #parsed_alarm_datetime.strftime("%A %d %B %Y, %I:%M:%S %p")
        
        if parsed_alarm_datetime == None:
            text_alarm_status.text_color = "red"
            text_alarm_status.value = f"Couldn't parse a date from string \"{alarm_time_str}\""
            return
        
        if parsed_alarm_datetime < datetime.now():
            text_alarm_status.text_color = "red"
            text_alarm_status.value = "Can't set alarm to ring in the past"
            return
        
        #window_blinds.go_to_closed() #starts the blinds closing, does not block
        
        text_alarm_status.text_color = "black"
        
        
        def alarm_tick():
            timedelta = parsed_alarm_datetime - datetime.now()
            total_seconds = timedelta.total_seconds()
            if total_seconds > 0:
                hours, remainder = divmod(total_seconds, 60*60)
                minutes, seconds = divmod(remainder, 60)
                text_alarm_status.value = f"Alarm will ring in {hours} hr {minutes} min {seconds} sec"
                guizero_app.after(1000, alarm_tick)
            else:
                text_alarm_status.value = "Alarm finished"
                window_blinds.go_to_open()
            
            
        alarm_tick()
        
        
        
       
    guizero.PushButton(box_custom_alarm, text="Go", command=update_custom_alarm)
    
        
    guizero_app.display() #blocks until the guizero window is closed
 

     

if __name__ == '__main__':
    make_end_user_gui()
