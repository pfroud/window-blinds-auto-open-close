def main():
    import board
    import dateparser
    from datetime import datetime
    from neopixel_ring_clock import NeopixelRingClock
    clock = NeopixelRingClock(board.D18, 35, 2)

    now = datetime.now()
    now_is_pm = now.hour > 11
    am_or_pm_str = "PM" if now_is_pm else "AM"
    am_or_pm_str_inverse = "AM" if now_is_pm else "PM"
    alarm_region_key = "testing"
    DATETIME_FORMAT_STRING = "%A %d %B %Y, %I:%M:%S %p"

    # 3
    print("Test case 1: alarm both starts and ends in the present halfday.")
    start = dateparser.parse("at 4 " + am_or_pm_str + " today").astimezone()
    end = dateparser.parse("at 8 " + am_or_pm_str + " today").astimezone()
    clock.put_alarm_region(alarm_region_key, start, end)
    clock.update()
    print("start = " + start.strftime(DATETIME_FORMAT_STRING))
    print("  end = " + end.strftime(DATETIME_FORMAT_STRING))
    input("Check if it looks okay, then press enter.")
    print()

    # 3
    print("Test case 2: alarm starts in a past halfday and ends in the present halfday.")
    start = dateparser.parse("at 1 PM yesterday").astimezone()
    end = dateparser.parse("at 4 " + am_or_pm_str + " today").astimezone()
    clock.put_alarm_region(alarm_region_key, start, end)
    clock.update()
    print("start = " + start.strftime(DATETIME_FORMAT_STRING))
    print("  end = " + end.strftime(DATETIME_FORMAT_STRING))
    input("Check if it looks okay, then press enter.")

    # 3
    print("Test case 3: alarm starts in a past halfday and ends a future halfday.")
    start = dateparser.parse("at 1 PM yesterday").astimezone()
    end = dateparser.parse("at 4 PM tomorrow").astimezone()
    clock.put_alarm_region(alarm_region_key, start, end)
    clock.update()
    print("start = " + start.strftime(DATETIME_FORMAT_STRING))
    print("  end = " + end.strftime(DATETIME_FORMAT_STRING))
    input("Check if it looks okay, then press enter.")

    # 3
    print("Test case 3: alarm starts in the present halfday and ends a future halfday.")
    start = dateparser.parse("at 5 " + am_or_pm_str + " today").astimezone()
    end = dateparser.parse("at 4 PM tomorrow").astimezone()
    clock.put_alarm_region(alarm_region_key, start, end)
    clock.update()
    print("start = " + start.strftime(DATETIME_FORMAT_STRING))
    print("  end = " + end.strftime(DATETIME_FORMAT_STRING))
    input("Check if it looks okay, then press enter.")

    clock.all_off()


if __name__ == '__main__':
    main()
