#!/usr/bin/env python3

import os
import guizero
from datetime import datetime
from datetime import timedelta
import requests
from neopixel_ring_clock import NeopixelRingClock
from window_blinds import WindowBlinds
import traceback
import dateparser
import board

# See https://strftime.org/
DATETIME_FORMAT_STRING = "%A %d %B %Y, %I:%M:%S %p"

def timedelta_split(td):
    # Apparently timedelta doesn't have a string formatting function, we need to DIY it
    split = str(td).split(":")
    hours = int(split[0])
    minutes = int(split[1])
    seconds = round(float(split[2]))
    if seconds == 60:
        seconds = 0
        minutes += 1
    if minutes == 60:
        minutes = 0
        hours += 1
    return hours, minutes, seconds

def vertical_spacer(parent, height):
    guizero.Box(parent, height=str(height))

def get_sunrise_datetime(date):
    # See https://sunrise-sunset.org/api/
    url = "https://api.sunrise-sunset.org/json"
    params = {
            # coordinates for the City of Santa Clara, California
            "lat": 37.354444,
            "lng": -121.969167,
            
            # When formatted==1, the response is in "HH:MM:SS AM" format.
            # When formatted==0, the response is in ISO 8601 format with times in UTC,
            #   which is "YYYY-MM-DDTHH:MM:SS+00:00".
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
    vertical_spacer(guizero_app, 10)
    
    window_blinds_direction_pin = 12 #GPIO pin 12 == Raspberry Pi pin 32
    window_blinds_pwm_pin = 16 #GPIO pin 16 == Raspberry Pi pin 36
    window_blinds = WindowBlinds(guizero_app, window_blinds_direction_pin, window_blinds_pwm_pin)
     
    
    neopixel_pin = board.D18 #GPIO pin 18 == Raspberry Pi pin 12
    led_count = 35
    maximum_duty_cycle = 10 #limit the led brightness
    clock = NeopixelRingClock(neopixel_pin, led_count, maximum_duty_cycle)
    clock.update()
    
    daily_alarm_close_datetime = None
    daily_alarm_open_datetime = None
    one_time_alarm_open_datetime = None
    
    ########################################################################
    #################### Create GUI for daily alarm ########################
    ########################################################################
    box_daily_alarm = guizero.Box(guizero_app, width="fill")
    box_daily_alarm.set_border(1, "#aaaaaa")
    guizero.Text(box_daily_alarm, text="Daily alarm")
    vertical_spacer(box_daily_alarm, 10)
    
    # How long before sunrise to close the blinds
    box_close_blinds_time = guizero.Box(box_daily_alarm)
    guizero.Text(box_close_blinds_time, text="Close blinds ", align="left")
    textbox_minutes_before_sunrise = guizero.TextBox(box_close_blinds_time, align="left", text="60")
    guizero.Text(box_close_blinds_time, text=" minutes before sunrise.", align="left")
    
    # What time to open the blinds afterwards
    box_open_blinds_time = guizero.Box(box_daily_alarm)
    guizero.Text(box_open_blinds_time, text="Open blinds at ", align="left")
    textbox_open_blinds_time = guizero.TextBox(box_open_blinds_time, text="11 am", align="left")
    guizero.Text(box_open_blinds_time, text=".", align="left")
    
    text_daily_alarm_status = guizero.Text(box_daily_alarm, text="Click the button below to set the daily alarm.")
    vertical_spacer(box_daily_alarm, 10)
    text_daily_alarm_status2 = guizero.Text(box_daily_alarm, text="Second line of status")
    vertical_spacer(box_daily_alarm, 10)
    text_daily_alarm_status3 = guizero.Text(box_daily_alarm, text="Third line of status")
    
    def set_daily_alarm():
            
        # Close the blinds a user-specified amount of time before sunrise.
        # Open the blinds at a user specified absolute time.
        
        now = datetime.now()
        today = now.date()
        
        ######## when to close the blinds - get from sunrise API, then subtract a user-specified duration
        
        is_pm = now.hour > 11
        if is_pm:
            # Sunrise is always in the AM, so we want to schedule the alarm for tomorrow
            date_to_get_sunrise_for = today + timedelta(days=1)
        else:
            # We want to schedule the alarm for today
            date_to_get_sunrise_for = today
        
        nonlocal daily_alarm_close_datetime
        
        
        sunrise_datetime = get_sunrise_datetime(date_to_get_sunrise_for) #TODO find way to not hang GUI when this is running
        if sunrise_datetime is None:
            text_daily_alarm_status.text_color = "red"
            text_daily_alarm_status.value = "Couldn't get sunrise datetime"
            daily_alarm_close_datetime = None
            return
        
        minutes_before_sunrise = int(textbox_minutes_before_sunrise.value)
        daily_alarm_close_datetime = (sunrise_datetime - timedelta(minutes=minutes_before_sunrise)).astimezone()
        
        
        #################### when to open the blinds - get an absolute time from user
        
        open_at_datetime_parsed = dateparser.parse(textbox_open_blinds_time.value).astimezone()
        
        nonlocal daily_alarm_open_datetime
        
        if open_at_datetime_parsed is None:
            text_daily_alarm_status.text_color = "red"
            text_daily_alarm_status.value = "Couldn't parse date from string"
            daily_alarm_open_datetime = None
            return
        
        daily_alarm_open_datetime = datetime.combine(date_to_get_sunrise_for, open_at_datetime_parsed.time()).astimezone()
        
        if daily_alarm_open_datetime <= daily_alarm_close_datetime:
            text_daily_alarm_status.text_color = "red"
            text_daily_alarm_status.value = "Trying to set blinds to open before they close:" + \
                "\ndaily_alarm_open_datetime = " + daily_alarm_open_datetime.strftime(DATETIME_FORMAT_STRING) + \
                "\ndaily_alarm_close_datetime = " + daily_alarm_close_datetime.strftime(DATETIME_FORMAT_STRING)
            daily_alarm_open_datetime = None
            return
        
     
        
        #clock.put_alarm_region("one-time", daily_alarm_close_datetime, daily_alarm_open_datetime)
        
        daily_alarm_close_datetime = dateparser.parse("in 5 seconds").astimezone()
        daily_alarm_open_datetime = dateparser.parse("in 30 seconds").astimezone()
        
        text_daily_alarm_status.text_color = "black"
        text_daily_alarm_status.value = \
            "\nSunrise is:\n"+ sunrise_datetime.strftime(DATETIME_FORMAT_STRING) + \
            "\n\nClose blinds at:\n" + daily_alarm_close_datetime.strftime(DATETIME_FORMAT_STRING) + \
            "\n\nThen open blinds at:\n" + daily_alarm_open_datetime.strftime(DATETIME_FORMAT_STRING)
    
    guizero.PushButton(box_daily_alarm, text="Set daily alarm", command=set_daily_alarm)
    
    
    guizero.Box(guizero_app, height="40")
    
    #################################################################
    ################## Create gui for a one-time alarm ##############
    #################################################################
    box_one_time_alarm = guizero.Box(guizero_app, width="fill")
    box_one_time_alarm.set_border(1, "#aaaaaa")
    guizero.Text(box_one_time_alarm, text="One-time alarm")
    vertical_spacer(box_one_time_alarm, 10)
    
    box_one_time_alarm_time = guizero.Box(box_one_time_alarm)
    guizero.Text(box_one_time_alarm_time, text="Close blinds now, then open blinds ", align="left")
    textbox_one_time_alarm = guizero.TextBox(box_one_time_alarm_time, text="in 20 seconds", align="left", width=20)
    guizero.Text(box_one_time_alarm_time, text=".", align="left")
    
    text_one_time_alarm_status = guizero.Text(box_one_time_alarm, text="Click the button below to set a one-time alarm.")
    
    def set_one_time_alarm():
        parsed_datetime = dateparser.parse(textbox_one_time_alarm.value).astimezone()
        now = datetime.now().astimezone()
        nonlocal one_time_alarm_open_datetime
        
        if parsed_datetime is None:
            text_one_time_alarm_status.text_color = "red"
            text_one_time_alarm_status.value = "Couldn't parse date from string"
            one_time_alarm_open_datetime = None
            return
        
        total_seconds = (parsed_datetime - now).total_seconds()
        if total_seconds < 1:
            text_one_time_alarm_status.text_color = "red"
            text_one_time_alarm_status.value = "Can't set alarm to ring in the past"
            one_time_alarm_open_datetime = None
            return
            
        if total_seconds >= 60*60*24:
            text_one_time_alarm_status.text_color = "red"
            text_one_time_alarm_status.value = "Setting alarm to ring more than one day in the future is not supported"
            one_time_alarm_open_datetime = None
            return
        
        one_time_alarm_open_datetime = parsed_datetime
        window_blinds.go_to_closed() #starts the blinds closing, returns immediately, does not block
        clock.put_alarm_region("one-time", now, one_time_alarm_open_datetime)
        text_one_time_alarm_status.text_color = "black"
        text_one_time_alarm_status.value = "Submitted"
    
    guizero.PushButton(box_one_time_alarm, text="Set one-time alarm", command=set_one_time_alarm)    
    
    
    def tick():
        now = datetime.now().astimezone()
        
        nonlocal one_time_alarm_open_datetime
        nonlocal daily_alarm_close_datetime
        nonlocal daily_alarm_open_datetime
        
        if daily_alarm_close_datetime is not None:
            timedelta_to_daily_alarm_close = daily_alarm_close_datetime - now
            total_seconds = timedelta_to_daily_alarm_close.total_seconds()
            if total_seconds > 0:
                hours, minutes, seconds = timedelta_split(timedelta_to_daily_alarm_close)
                text_daily_alarm_status2.value = f"Blinds will close in {hours} hr {minutes} min {seconds} sec"
            else:
                text_daily_alarm_status2.value = f"Blinds closed at\n{now.strftime(DATETIME_FORMAT_STRING)}."
                daily_alarm_close_datetime = None
                window_blinds.go_to_closed()
            
        if daily_alarm_open_datetime is not None:
            timedelta_to_daily_alarm_open = daily_alarm_open_datetime - now
            total_seconds = timedelta_to_daily_alarm_open.total_seconds()
            if total_seconds > 0:
                hours, minutes, seconds = timedelta_split(timedelta_to_daily_alarm_open)
                text_daily_alarm_status3.value = f"Blinds will open in {hours} hr {minutes} min {seconds} sec"
            else:
                text_daily_alarm_status3.value =  f"Blinds opened at\n{now.strftime(DATETIME_FORMAT_STRING)}."
                daily_alarm_open_datetime = None
                window_blinds.go_to_open()
        
        if one_time_alarm_open_datetime is not None:
            timedelta_to_one_time_alarm_open = one_time_alarm_open_datetime - now
            total_seconds = timedelta_to_one_time_alarm_open.total_seconds()
            if total_seconds > 0:
                hours, minutes, seconds = timedelta_split(timedelta_to_one_time_alarm_open)
                text_one_time_alarm_status.value = f"One-time alarm will ring in {hours} hr {minutes} min {seconds} sec"
            else:
                text_one_time_alarm_status.value = f"One-time alarm rang at\n{now.strftime(DATETIME_FORMAT_STRING)}."
                one_time_alarm_open_datetime = None
                clock.remove_alarm_region("one-time")
                window_blinds.go_to_open()
        
        clock.update()
        
        
    guizero_app.repeat(1000, tick)
    guizero_app.display() #blocks until the guizero window is closed
    window_blinds.stop()
    clock.all_off()
 

if __name__ == '__main__':
    if os.geteuid() != 0:
        exit(__file__+": fatal: Need to run the script as root (use sudo) because using Neopixels accesses GPIO.")
    main()
