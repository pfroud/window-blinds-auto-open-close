# -*- coding: utf-8 -*-
from neopixel import NeoPixel
from datetime import datetime
from datetime import time
from datetime import timedelta

DATETIME_FORMAT_STRING = "%A %d %B %Y, %I:%M:%S %p"


class NeopixelRingClock:
    def __init__(self, pin, led_count, max_brightness):
        self.neopixels = NeoPixel(pin, led_count)
        self.max_brightness = max_brightness
        self.led_count = led_count
        self.alarm_regions = {}
        self.debug_printouts = False

    def set_max_brightness(self, new_max_brightness):
        self.max_brightness = new_max_brightness
        self.tick()

    def put_alarm_region(self, key, datetime_start, datetime_end):
        if datetime_start < datetime_end:
            self.alarm_regions[key] = [datetime_start, datetime_end]
        else:
            print(f"{__file__}: Cannot put alarm region for key \"{key}\": start is after end. start = {datetime_start}; end = {datetime_end}.")

        # reject if the difference is more than 12 hours, to prevent an entire
        # halfday being green

    def remove_alarm_region(self, key):
        del self.alarm_regions[key]

    def _get_led_duty_cycle_for_time_ratio(self, led_index, time_ratio):

        led_ratio = led_index / self.led_count
        led_distance = abs(led_ratio - time_ratio)

        # Graph of LED duty cycle vs distance the LED is to the clock hand
        #
        #   max_brightness| \
        # d               |  \
        # u               |   \
        # t               |    \
        # y               |     \
        #                 |      \
        # c               |       \
        # y               |        \
        # c               |         \
        # l               |          \
        # e               |           \
        #                0+-----------------
        #                 0       (1/led_count)
        #                   distance

        rise = -self.max_brightness
        run = 1 / self.led_count
        slope = rise / run

        return max(0, slope * led_distance + self.max_brightness)

    def _get_ratios_for_datetime(self, the_datetime):
        hour = the_datetime.hour
        if hour > 11:
            # Change 24-hour time to 12-hour time.
            # 12 P.M. becomes hour zero, 1 P.M. becomes hour one, etc.
            hour = hour - 12
        minute = the_datetime.minute
        second = the_datetime.second

        second_ratio = second / 60
        minute_ratio = (minute + second_ratio) / 60
        hour_ratio = (hour + minute_ratio) / 12

        return hour_ratio, minute_ratio, second_ratio

    def update(self):
        datetime_now = datetime.now().astimezone()

        ratio_hour, ratio_minute, ratio_second = self._get_ratios_for_datetime(
            datetime_now)

        for i in range(0, self.led_count):

            if i == 0 and datetime_now.hour == 11 and datetime_now.minute > 30:
                # The hour hand has almost gone back around to 12 o'clock.
                # We want the LED with index zero to start fading in.
                #
                # The for loop will set i to 0, 1, ..., led_count-2, led_count-1.
                #
                # We will do the computation for an imaginary extra LED, at index
                # led_count, but assign the result to the LED at index zero.
                led_index_to_compute = self.led_count
                led_index_to_set = 0
            else:
                led_index_to_compute = i
                led_index_to_set = i

            red = self._get_led_duty_cycle_for_time_ratio(
                led_index_to_compute, ratio_hour)
            blue = self._get_led_duty_cycle_for_time_ratio(
                led_index_to_compute, ratio_minute)

            is_led_inside_any_region = False
            datetime_start_of_today = datetime_now.replace(hour=0, minute=0)
            datetime_noon_today = datetime_now.replace(hour=12, minute=0)
            datetime_start_of_next_day = datetime_start_of_today + \
                timedelta(days=1)

            if datetime_now.hour < 12:
                # AM
                datetime_halfday_start = datetime_start_of_day
                datetime_halfday_end = datetime_noon_today
            else:
                # PM
                datetime_halfday_start = datetime_noon_today
                datetime_halfday_end = datetime_start_of_next_day

            led_ratio = led_index_to_compute / self.led_count
            for key, array_of_datetimes in self.alarm_regions.items():
                datetime_region_start = array_of_datetimes[0]
                datetime_region_end = array_of_datetimes[1]

                if datetime_region_start > datetime_region_end:
                    print(
                        f"Malformed alarm region for key \"{key}\": start is after end. start = {datetime_region_start}; end = {datetime_region_end}.")
                    continue

                if i == 0 and self.debug_printouts:
                    print(
                        f"region [{datetime_region_start.strftime(DATETIME_FORMAT_STRING)}] --> [{datetime_region_end.strftime(DATETIME_FORMAT_STRING)}]")

                hour_ratio_region_start = self._get_ratios_for_datetime(datetime_region_start)[
                    0]
                hour_ratio_region_end = self._get_ratios_for_datetime(datetime_region_end)[
                    0]

                did_region_start_in_past_halfday = datetime_region_start < datetime_halfday_start
                does_region_start_in_present_halfday = datetime_halfday_start <= datetime_region_start < datetime_halfday_end
                is_led_after_region_start = did_region_start_in_past_halfday or \
                    (does_region_start_in_present_halfday and led_ratio >
                     hour_ratio_region_start)

                will_region_end_in_future_halfday = datetime_region_end >= datetime_halfday_end
                does_region_end_in_present_halfday = datetime_halfday_start <= datetime_region_end < datetime_halfday_end
                is_led_before_region_end = will_region_end_in_future_halfday or \
                    (does_region_end_in_present_halfday and led_ratio <
                     hour_ratio_region_end)

                if self.debug_printouts:
                    print(f"    i={i:2}: ")

                is_led_inside_any_region = is_led_after_region_start and is_led_before_region_end

            green = self.max_brightness if is_led_inside_any_region else 0
            self.neopixels[led_index_to_set] = (red, green, blue)

    def all_off(self):
        for i in range(0, self.led_count):
            self.neopixels[i] = (0, 0, 0)
