#!/usr/bin/env python3


import guizero
from datetime import datetime
from datetime import timedelta
import requests
from neopixel_ring_clock import NeopixelRingClock
from window_blinds import WindowBlinds
import traceback
import dateparser
import board


DATETIME_FORMAT_STRING = "%A %d %B %Y, %I:%M:%S %p"


def get_sunrise_datetime(date):
    # see https://sunrise-sunset.org/api
    
    url = "https://api.sunrise-sunset.org/json"
    params = {
            # coordinates for Santa Clara, California (city not county)
            "lat": 37.354444,
            "lng": -121.969167,
            
            # when formatted==0, the response is in ISO 8601 format
            "formatted": 0,
            "date": date.isoformat()
        }
    
    
    try:
        response = requests.get(url, params=params).json()
    except requests.exceptions.RequestException as e:
        traceback.print_exc()
        return None
        
    
    if response["status"] == "OK":
        sunrise_string = response["results"]["sunrise"]
        # The returned time is in UTC, so we need to add timezone information
        return datetime.fromisoformat(sunrise_string).astimezone()
    else:
        print("sunrise-sunset.org API call failed, response status is ", response["status"])
        return None



def main():
    guizero_app = guizero.App(title="Window blinds thing")
    
    window_blinds_direction_pin = 12 #GPIO 12 = rpi pin 32
    window_blinds_pwm_pin = 16 #GPIO 16 = rpi pin 36
    window_blinds = WindowBlinds(guizero_app, window_blinds_direction_pin, window_blinds_pwm_pin)
     
    
    # create the addressable led abstraction
    neopixel_pin = board.D18 #GPIO 18 = rpi pin 12
    led_count = 35
    brightness_max = 10
    clock = NeopixelRingClock(neopixel_pin, led_count, brightness_max)
    clock.update_time_and_display()
    
    daily_alarm_close_datetime = None
    daily_alarm_open_datetime = None
    
    one_time_alarm_open_datetime = None
    
    
    ########################################################################
    #################### create GUI for daily alarm ########################
    ########################################################################
    guizero.Box(guizero_app, height="10")
    box_daily_alarm = guizero.Box(guizero_app, width="fill")
    box_daily_alarm.set_border(1, "#aaaaaa")
     
    guizero.Text(box_daily_alarm, text="Daily alarm")
    guizero.Box(box_daily_alarm, height="10")
    
    # how long before sunrise to close the blinds
    box_close_blinds_time = guizero.Box(box_daily_alarm)
    guizero.Text(box_close_blinds_time, text="Close blinds ", align="left")
    textbox_minutes_before_sunrise = guizero.TextBox(box_close_blinds_time, align="left", text="60")
    guizero.Text(box_close_blinds_time, text="minutes before sunrise.", align="left")
    
    # what time to open the blinds afterwards
    box_open_blinds_time = guizero.Box(box_daily_alarm)
    guizero.Text(box_open_blinds_time, text="Open blinds at ", align="left")
    textbox_open_blinds_time = guizero.TextBox(box_open_blinds_time, text="11 am", align="left")
    guizero.Text(box_open_blinds_time, text=".", align="left")
    
    text_daily_alarm_status = guizero.Text(box_daily_alarm, text="Click the button below to set the daily alarm")
    
    def set_daily_alarm():
            
        # Close the blinds a user-specified amount of time before sunrise.
        # Open the blinds at a user specified absolute time.
        
        now = datetime.now()
        today = now.date()
        
        ######## when to close the blinds - get from sunrise API
        
        is_pm = now.hour >= 12
        
        if is_pm:
            # schedule the alarm for tomorrow
            date_to_get_sunrise_for = today + timedelta(days=1)
        else:
            # schedule the alarm for today
            date_to_get_sunrise_for = today
        
        nonlocal daily_alarm_close_datetime
        
        text_daily_alarm_status.value = "Fetching sunrise time..."
        sunrise_datetime = get_sunrise_datetime(date_to_get_sunrise_for)
        text_daily_alarm_status.value = "Back from fetching sunrise time"
        if sunrise_datetime is None:
            text_daily_alarm_status.text_color = "red"
            text_daily_alarm_status.value = "Couldn't get sunrise datetime"
            daily_alarm_close_datetime = None
            return
        
        minutes_before_sunrise = int(textbox_minutes_before_sunrise.value)
        
        
        daily_alarm_close_datetime = sunrise_datetime - timedelta(minutes=minutes_before_sunrise)
        
        
        #################### when to open the blinds - get from user
        
        open_at_datetime_parsed = dateparser.parse(textbox_open_blinds_time.value).astimezone()
        
        nonlocal daily_alarm_open_datetime
        
        if open_at_datetime_parsed is None:
            text_daily_alarm_status.text_color = "red"
            text_daily_alarm_status.value = "Couldn't parse date from string"
            daily_alarm_open_datetime = None
            return
        
        if open_at_datetime_parsed <= daily_alarm_close_datetime:
            text_daily_alarm_status.text_color = "red"
            text_daily_alarm_status.value = "Trying to set blinds to open before they close"
            daily_alarm_open_datetime = None
            return
        
        daily_alarm_open_datetime = datetime.combine(date_to_get_sunrise_for, open_at_datetime_parsed.time()).astimezone()
          
        text_daily_alarm_status.text_color = "black"
        text_daily_alarm_status.value = \
            "Sunrise is:\n"+ sunrise_datetime.strftime(DATETIME_FORMAT_STRING) + \
            "\n\nClose blinds at:\n" + daily_alarm_close_datetime.strftime(DATETIME_FORMAT_STRING) + \
            "\n\nThen open blinds at:\n" + daily_alarm_open_datetime.strftime(DATETIME_FORMAT_STRING)
    
    guizero.PushButton(box_daily_alarm, text="Set daily alarm", command=set_daily_alarm)
    
    
    guizero.Box(guizero_app, height="40")
    
    #################################################################
    ################## create gui for a one-time alarm ##############
    #################################################################
    box_one_time_alarm = guizero.Box(guizero_app, width="fill")
    box_one_time_alarm.set_border(1, "#aaaaaa")
    guizero.Text(box_one_time_alarm, text="One-time alarm")
    guizero.Box(box_one_time_alarm, height="10")
    
    box_one_time_alarm_time = guizero.Box(box_one_time_alarm)
    guizero.Text(box_one_time_alarm_time, text="Close blinds now, then open blinds ", align="left")
    textbox_one_time_alarm = guizero.TextBox(box_one_time_alarm_time, text="in 20 seconds", align="left", width=20)
    guizero.Text(box_one_time_alarm_time, text=".", align="left")
    
    text_alarm_status = guizero.Text(box_one_time_alarm, text="Click the button below to set a one-time alarm")
    
    def set_one_time_alarm():
        parsed_datetime = dateparser.parse(textbox_one_time_alarm.value)
        
        nonlocal one_time_alarm_open_datetime
        
        if parsed_datetime is None:
            text_alarm_status.text_color = "red"
            text_alarm_status.value = "Couldn't parse date from string"
            one_time_alarm_open_datetime = None
            return
        
        if parsed_datetime < datetime.now():
            text_alarm_status.text_color = "red"
            text_alarm_status.value = "Can't set alarm to ring in the past"
            one_time_alarm_open_datetime = None
            return
        
        one_time_alarm_open_datetime = parsed_datetime
        window_blinds.go_to_closed() #starts the blinds closing, does not block
        text_alarm_status.text_color = "black"
        text_alarm_status.value = "Submitted"
    
    guizero.PushButton(box_one_time_alarm, text="Set one-time alarm", command=set_one_time_alarm)    
    
    
    def tick():
        now = datetime.now()
        
        nonlocal one_time_alarm_open_datetime
        nonlocal daily_alarm_close_datetime
        nonlocal daily_alarm_open_datetime
        
        if daily_alarm_close_datetime is not None and daily_alarm_open_datetime is not None:
            pass
        
        if one_time_alarm_open_datetime is not None:
            timedelta_to_one_shot_alarm_open = one_time_alarm_open_datetime - now
            total_seconds = timedelta_to_one_shot_alarm_open.total_seconds()
            if total_seconds > 0:
                # apparently there is no string formatting for timedeltas, we have to diy it
                split = str(timedelta_to_one_shot_alarm_open).split(":")
                hours = int(split[0])
                minutes = int(split[1])
                seconds = round(float(split[2]))
                if seconds == 60:
                    seconds = 0
                    minutes += 1
                if minutes == 60:
                    minutes = 0
                    hours += 1
                
                text_alarm_status.value = f"Alarm will ring in {hours} hr {minutes} min {seconds} sec"
            else:
                text_alarm_status.value = "Alarm rang at " + now.strftime(DATETIME_FORMAT_STRING)
                one_time_alarm_open_datetime = None
                window_blinds.go_to_open()
        
        clock.update_time_and_display
        
        
    guizero_app.repeat(1000, tick)
    guizero_app.display() #blocks until the guizero window is closed
 

if __name__ == '__main__':
    main()
