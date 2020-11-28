# -*- coding: utf-8 -*-
from neopixel import NeoPixel
from datetime import datetime

class NeopixelRingClock:
    def __init__(self, pin, led_count, max_brightness):
        self.neopixels = NeoPixel(pin, led_count)
        self.max_brightness = max_brightness
        self.led_count = led_count
        self.alarm_regions = {
            #"test": [
            #    datetime(2020, 10, 30, 2, 0, 0),
            #    datetime(2020, 10, 30, 5, 0, 0)
            #]
        }
         
    def set_max_brightness(self, new_max_brightness):
        self.max_brightness = new_max_brightness
        self.tick()
         
    def put_alarm_region(self, key, datetime_start, datetime_end):
        if datetime_start < datetime_end:
            self.alarm_regions[key] = [datetime_start, datetime_end]
        else:
            print(f"Cannot put alarm region for key \"{key}\": start is after end. start = {datetime_start}; end = {datetime_end}.")
         
    def remove_alarm_region(self, key):
        del self.alarm_regions[key]
    
    def _get_duty_cycle_for_ratio(self, led_index, time_ratio):
        
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
        is_pm = hour > 11
        if is_pm:
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
        now = datetime.now()
        now_is_pm = now.hour > 11
        
        hour_ratio, minute_ratio, second_ratio = self._get_ratios_for_datetime(now)
        
        for i in range(0, self.led_count):
            
            if i==0 and now.hour==11 and now.minute>30:
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
                       
            red = self._get_duty_cycle_for_ratio(led_index_to_compute, hour_ratio)
            blue = self._get_duty_cycle_for_ratio(led_index_to_compute, minute_ratio)
            
            green = 0
            for key, array_of_datetimes in self.alarm_regions.items():
                region_start_datetime = array_of_datetimes[0]
                region_end_datetime = array_of_datetimes[1]
                
                if region_start_datetime > region_end_datetime:
                    print(f"Malformed alarm region for key \"{key}\": start is after end. start = {region_start_datetime}; end = {region_end_datetime}.")
                    continue
                
                region_start_hour_ratio, not_used, not_used = self._get_ratios_for_datetime(region_start_datetime)
                region_end_hour_ratio, not_used, not_used = self._get_ratios_for_datetime(region_end_datetime)
                led_ratio = led_index_to_compute / self.led_count
                
                region_start_is_pm = region_start_datetime.hour > 11
                region_end_is_pm = region_end_datetime.hour > 11
                
               
                if led_ratio <= region_end_hour_ratio and region_start_is_pm != now_is_pm:
                    # The region started in the previous halfday, and ends this halfday.
                    # We need to show the rest of it.
                    green = self.max_brightness
                
                elif led_ratio >= region_start_hour_ratio:
                    # we definitley need to start. But when do we stop?
                    if region_end_is_pm == now_is_pm:
                        # The alarm ends this halfday. 
                        if led_ratio <= region_end_hour_ratio:
                            # We are inside the region.
                            green = self.max_brightness
                        else:
                            # We have passed the end of the region.
                            green = 0
                    else :
                        # The alarm ends the next halfday.
                        # Shade all the rest of the LEDs
                        green = self.max_brightness
                else:
                    # The alarm does not happen this halfday.
                    green = 0
               
            
            self.neopixels[led_index_to_set] = (red, green, blue)
