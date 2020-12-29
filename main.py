#!/usr/bin/env python3

import os
import guizero
import requests
import traceback
import dateparser
import board
import suntime
from datetime import datetime
from datetime import timedelta
from datetime import date
from durations import Duration
from neopixel_ring_clock import NeopixelRingClock
from window_blinds import WindowBlinds

# See https://strftime.org/
DATETIME_FORMAT_STRING = "%A %d %B %Y, %I:%M:%S %p"


def timedelta_split(td):
    # Apparently timedelta doesn't have a string formatting function,
    # we need to DIY it.
    # TODO support durations greater or equal to one day
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


def main():
    guizero_app = guizero.App(
        title="Window blinds automatic opener & closer",
        width=500,
        height=700)
    vertical_spacer(guizero_app, 10)

    pin_window_blinds_direction = 12  # GPIO pin 12 == Raspberry Pi pin 32
    pin_window_blinds_pwm = 16  # GPIO pin 16 == Raspberry Pi pin 36
    window_blinds = WindowBlinds(
        guizero_app, pin_window_blinds_direction,
        pin_window_blinds_pwm)

    pin_neopixel = board.D18  # GPIO pin 18 == Raspberry Pi pin 12
    led_count = 35
    maximum_duty_cycle = 5  # limit the led brightness
    neopixel_ring_clock = NeopixelRingClock(pin_neopixel, led_count,
                                            maximum_duty_cycle)
    neopixel_ring_clock.update()

    datetime_daily_alarm_close = None
    datetime_daily_alarm_open = None
    datetime_one_time_alarm_open = None

    vertical_spacer(guizero_app, 10)
    box_brightness = guizero.Box(guizero_app, width="fill")
    box_brightness.set_border(1, "#aaaaaa")
    guizero.Text(box_brightness, text="LED brightness").tk.configure(
        font=("Liberation Sans", 12, "bold"))

    def handle_brightness_changed():
        neopixel_ring_clock.max_brightness = int(slider_brightness.value)
        neopixel_ring_clock.update()
    slider_brightness = guizero.Slider(box_brightness, start=0, end=255,
                                       command=handle_brightness_changed, width="fill")
    slider_brightness.value = maximum_duty_cycle

    vertical_spacer(guizero_app, 40)
    ########################################################################
    #################### Create GUI for daily alarm ########################
    ########################################################################
    box_daily_alarm = guizero.Box(guizero_app, width="fill")
    box_daily_alarm.set_border(1, "#aaaaaa")
    guizero.Text(box_daily_alarm, text="Daily alarm").tk.configure(
        font=("Liberation Sans", 12, "bold"))
    vertical_spacer(box_daily_alarm, 10)

    # Duration before sunrise to close the blinds
    box_close_blinds_time = guizero.Box(box_daily_alarm)
    guizero.Text(box_close_blinds_time, text="Close the blinds ", align="left")
    textbox_duration_before_sunrise = guizero.TextBox(box_close_blinds_time,
                                                      align="left", text="1 hour")
    guizero.Text(box_close_blinds_time, text=" before sunrise.",
                 align="left")

    # What time to open the blinds afterwards
    box_open_blinds_time = guizero.Box(box_daily_alarm)
    guizero.Text(
        box_open_blinds_time,
        text="Then, open the blinds at ",
        align="left")
    textbox_open_blinds_time = guizero.TextBox(box_open_blinds_time,
                                               text="11 AM", align="left")
    guizero.Text(box_open_blinds_time, text=".", align="left")

    text_daily_alarm_status = guizero.Text(box_daily_alarm,
                                           text="Click the button below to set the daily alarm.")
    vertical_spacer(box_daily_alarm, 10)
    text_daily_alarm_status2 = guizero.Text(box_daily_alarm,
                                            text="Second line of status")
    vertical_spacer(box_daily_alarm, 10)
    text_daily_alarm_status3 = guizero.Text(box_daily_alarm,
                                            text="Third line of status")

    def set_daily_alarm(for_date=None):
        # Close the blinds a user-specified amount of time before sunrise.
        # Open the blinds at a user specified absolute time.

        # Coordinates for the City of Santa Clara, California
        sun = suntime.Sun(37.354444, -121.969167)

        if for_date is None:
            # If the date to get the sunrise for isn't speficied,
            # schedule the blinds to open for the next future sunrise.
            datetime_now = datetime.now().astimezone()
            date_today = datetime_now.date()
            is_pm = datetime_now.hour > 11
            if is_pm:
                # Sunrise is always in the AM. If the current time is PM,
                # schedule the blinds to open for tomorrow's sunrise.
                date_tomorrow = date_today + timedelta(days=1)
                datetime_sunrise = sun.get_sunrise_time(
                    date_tomorrow).astimezone()

            else:
                # Check if sunrise already happened
                datetime_sunrise_today = sun.get_sunrise_time(
                    date_today).astimezone()

                if datetime_sunrise_today <= datetime_now:
                    # Sunrise already happened today. Schedule the blinds
                    # to open for tomorrow's sunrise.
                    date_tomorrow = date_today + timedelta(days=1)
                    datetime_sunrise = sun.get_sunrise_time(
                        date_tomorrow).astimezone()
                else:
                    # sunrise is in the future today
                    datetime_sunrise = datetime_sunrise_today

        else:
            # Use the date given in the keywork argument.
            datetime_sunrise = sun.get_sunrise_time(for_date).astimezone()

        nonlocal datetime_daily_alarm_close

        seconds_before_sunrise = Duration(
            textbox_duration_before_sunrise.value).to_seconds()
        datetime_daily_alarm_close = (datetime_sunrise -
                                      timedelta(seconds=seconds_before_sunrise)).astimezone()

        # When to open the blinds - get an absolute time from user.
        datetime_parsed_open_at = dateparser.parse(
            textbox_open_blinds_time.value).astimezone()

        nonlocal datetime_daily_alarm_open

        if datetime_parsed_open_at is None:
            text_daily_alarm_status.text_color = "red"
            text_daily_alarm_status.value = "Couldn't parse date from string"
            datetime_daily_alarm_open = None
            return

        datetime_daily_alarm_open = datetime.combine(datetime_sunrise.date(),
                                                     datetime_parsed_open_at.time()).astimezone()

        if datetime_daily_alarm_open <= datetime_daily_alarm_close:
            text_daily_alarm_status.text_color = "red"
            text_daily_alarm_status.value = \
                "Trying to set blinds to open before they close:" + \
                "\ndatetime_daily_alarm_open = " + \
                datetime_daily_alarm_open.strftime(DATETIME_FORMAT_STRING) + \
                "\ndatetime_daily_alarm_close = " + \
                datetime_daily_alarm_close.strftime(DATETIME_FORMAT_STRING)
            datetime_daily_alarm_open = None
            return

        neopixel_ring_clock.put_alarm_region("daily",
                                             datetime_daily_alarm_close, datetime_daily_alarm_open)

        text_daily_alarm_status.text_color = "black"
        text_daily_alarm_status.value = \
            "\nSunrise is:\n" + \
            datetime_sunrise.strftime(DATETIME_FORMAT_STRING) + \
            "\n\nClose blinds at:\n" + \
            datetime_daily_alarm_close.strftime(DATETIME_FORMAT_STRING) + \
            "\n\nThen open blinds at:\n" + \
            datetime_daily_alarm_open.strftime(DATETIME_FORMAT_STRING)

    guizero.PushButton(box_daily_alarm, text="Update daily alarm",
                       command=set_daily_alarm)

    vertical_spacer(guizero_app, 40)

    #################################################################
    ################## Create gui for a one-time alarm ##############
    #################################################################
    box_one_time_alarm = guizero.Box(guizero_app, width="fill")
    box_one_time_alarm.set_border(1, "#aaaaaa")
    guizero.Text(box_one_time_alarm,
                 text="One-time alarm").tk.configure(font=("Liberation Sans", 12, "bold"))
    vertical_spacer(box_one_time_alarm, 10)

    box_one_time_alarm_time = guizero.Box(box_one_time_alarm)
    guizero.Text(box_one_time_alarm_time,
                 text="Close blinds now, then open blinds ", align="left")
    textbox_one_time_alarm = guizero.TextBox(box_one_time_alarm_time,
                                             text="in 20 seconds", align="left", width=20)
    guizero.Text(box_one_time_alarm_time, text=".", align="left")

    text_one_time_alarm_status = guizero.Text(box_one_time_alarm,
                                              text="Click the button below to set a one-time alarm.")

    def set_one_time_alarm():
        datetime_parsed = dateparser.parse(textbox_one_time_alarm.value) \
            .astimezone()
        datetime_now = datetime.now().astimezone()
        nonlocal datetime_one_time_alarm_open

        if datetime_parsed is None:
            text_one_time_alarm_status.text_color = "red"
            text_one_time_alarm_status.value = \
                "Couldn't parse date from string"
            datetime_one_time_alarm_open = None
            return

        total_seconds = (datetime_parsed - datetime_now).total_seconds()
        if total_seconds < 1:
            text_one_time_alarm_status.text_color = "red"
            text_one_time_alarm_status.value = \
                "Can't set alarm to ring in the past"
            datetime_one_time_alarm_open = None
            return

        if total_seconds >= 60 * 60 * 24:
            text_one_time_alarm_status.text_color = "red"
            text_one_time_alarm_status.value = "Setting alarm to ring " + \
                "more than one day in the future is not supported"
            datetime_one_time_alarm_open = None
            return

        datetime_one_time_alarm_open = datetime_parsed

        # Starts the blinds closing, returns immediately, does not block.
        window_blinds.go_to_closed()

        neopixel_ring_clock.put_alarm_region("one-time", datetime_now,
                                             datetime_one_time_alarm_open)
        text_one_time_alarm_status.text_color = "black"
        text_one_time_alarm_status.value = "Submitted"

    guizero.PushButton(box_one_time_alarm, text="Set one-time alarm",
                       command=set_one_time_alarm)

    def tick():
        datetime_now = datetime.now().astimezone()

        nonlocal datetime_one_time_alarm_open
        nonlocal datetime_daily_alarm_close
        nonlocal datetime_daily_alarm_open

        if datetime_daily_alarm_close is not None:
            timedelta_to_daily_alarm_close = \
                datetime_daily_alarm_close - datetime_now
            total_seconds = timedelta_to_daily_alarm_close.total_seconds()
            #print(f"total_seconds until daily alarm close: {total_seconds}")
            if total_seconds > 0:
                hours, minutes, seconds = \
                    timedelta_split(timedelta_to_daily_alarm_close)
                text_daily_alarm_status2.value = \
                    f"Blinds will close in {hours} hr {minutes} min {seconds} sec"
            else:
                #print("which is leq zero, so I am closing the blinds")
                text_daily_alarm_status2.value = \
                    f"Blinds closed at\n{datetime_now.strftime(DATETIME_FORMAT_STRING)}."
                datetime_daily_alarm_close = None
                window_blinds.go_to_closed()

        if datetime_daily_alarm_open is not None:
            timedelta_to_daily_alarm_open = \
                datetime_daily_alarm_open - datetime_now
            total_seconds = timedelta_to_daily_alarm_open.total_seconds()
            #print(f"total_seconds until daily alarm open:  {total_seconds}")
            if total_seconds > 0:
                hours, minutes, seconds = \
                    timedelta_split(timedelta_to_daily_alarm_open)
                text_daily_alarm_status3.value = \
                    f"Blinds will open in {hours} hr {minutes} min {seconds} sec"
            else:
                #print("    which is leq zero, so I am opening the blinds")
                text_daily_alarm_status3.value = \
                    f"Blinds opened at\n{datetime_now.strftime(DATETIME_FORMAT_STRING)}."
                datetime_daily_alarm_open = None
                window_blinds.go_to_open()
                date_tomorrow = date.today() + timedelta(days=1)
                set_daily_alarm(date_tomorrow)

        if datetime_one_time_alarm_open is not None:
            timedelta_to_one_time_alarm_open = \
                datetime_one_time_alarm_open - datetime_now
            total_seconds = timedelta_to_one_time_alarm_open.total_seconds()
            if total_seconds > 0:
                hours, minutes, seconds = \
                    timedelta_split(timedelta_to_one_time_alarm_open)
                text_one_time_alarm_status.value = f"One-time alarm will ring in {hours} hr {minutes} min {seconds} sec"
            else:
                text_one_time_alarm_status.value = f"One-time alarm rang at\n{datetime_now.strftime(DATETIME_FORMAT_STRING)}."
                datetime_one_time_alarm_open = None
                neopixel_ring_clock.remove_alarm_region("one-time")
                window_blinds.go_to_open()

        neopixel_ring_clock.update()

    set_daily_alarm()
    guizero_app.repeat(1000, tick)
    guizero_app.display()  # blocks until the guizero window is closed
    window_blinds.stop()
    neopixel_ring_clock.all_off()


if __name__ == '__main__':
    if os.geteuid() != 0:
        exit(__file__ + ": Need to run the script as root (use sudo) " +
             "because using Neopixels accesses GPIO.")
    main()
