import board
import os
import dateparser
from datetime import datetime
from neopixel_ring_clock import NeopixelRingClock


def main():
    pin_neopixel = board.D21  # GPIO pin 21 == Raspberry Pi pin 40
    led_count = 35
    maximum_duty_cycle = 255
    clock = NeopixelRingClock(pin_neopixel, led_count, maximum_duty_cycle)

    now = datetime.now()
    now_is_pm = now.hour > 11
    now_am_or_pm_str = "PM" if now_is_pm else "AM"
    now_am_or_pm_str_inverse = "AM" if now_is_pm else "PM"
    alarm_region_key = "testing"

    DATETIME_FORMAT_STRING = "%A %d %B %Y, %I:%M:%S %p"

    print("Test case 1: alarm both starts and ends in the present halfday.")
    start = dateparser.parse(
        "at 4 " +
        now_am_or_pm_str +
        " today").astimezone()
    end = dateparser.parse("at 8 " + now_am_or_pm_str + " today").astimezone()
    clock.put_alarm_region(alarm_region_key, start, end)
    clock.update()
    print("start = " + start.strftime(DATETIME_FORMAT_STRING))
    print("  end = " + end.strftime(DATETIME_FORMAT_STRING))
    input("Check if it looks okay, then press enter.")
    print()

    print("Test case 2: alarm starts in a past halfday and ends in the present halfday.")
    start = dateparser.parse("at 1 PM yesterday").astimezone()
    end = dateparser.parse("at 4 " + now_am_or_pm_str + " today").astimezone()
    clock.put_alarm_region(alarm_region_key, start, end)
    clock.update()
    print("start = " + start.strftime(DATETIME_FORMAT_STRING))
    print("  end = " + end.strftime(DATETIME_FORMAT_STRING))
    input("Check if it looks okay, then press enter.")
    print()

    print("Test case 3: alarm starts in a past halfday and ends a future halfday.")
    start = dateparser.parse("at 1 PM yesterday").astimezone()
    end = dateparser.parse("at 4 PM tomorrow").astimezone()
    clock.put_alarm_region(alarm_region_key, start, end)
    clock.update()
    print("start = " + start.strftime(DATETIME_FORMAT_STRING))
    print("  end = " + end.strftime(DATETIME_FORMAT_STRING))
    input("Check if it looks okay, then press enter.")
    print()

    print("Test case 3: alarm starts in the present halfday and ends a future halfday.")
    start = dateparser.parse(
        "at 5 " +
        now_am_or_pm_str +
        " today").astimezone()
    end = dateparser.parse("at 4 PM tomorrow").astimezone()
    clock.put_alarm_region(alarm_region_key, start, end)
    clock.update()
    print("start = " + start.strftime(DATETIME_FORMAT_STRING))
    print("  end = " + end.strftime(DATETIME_FORMAT_STRING))
    input("Check if it looks okay, then press enter.")

    print()
    print("End of tests.")
    clock.all_off()


if __name__ == '__main__':
    if os.geteuid() == 0:
        main()
    else:
        exit(__file__ + ": Need to run the script as root (use sudo) to access GPIO.")
