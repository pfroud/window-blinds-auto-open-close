# -*- coding: utf-8 -*-
from neopixel import NeoPixel
from datetime import datetime

class NeopixelRingClock:
    def __init__(self, pin, led_count, max_brightness):
         self.neopixels = NeoPixel(pin, led_count)
         self.max_brightness = max_brightness
         self.led_count = led_count
         
    def set_max_brightness(self, new_max_brightness):
         self.max_brightness = new_max_brightness
         self.tick()
         
    def display_time(self, hour, minute, second):
        second_ratio = second / 60
        minute_ratio = (minute + second_ratio) / 60
        hour_ratio = (hour + minute_ratio) / 12
        
        for i in range(0, self.led_count):
            
            if i==0 and hour==11 and minute>30:
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
            
            
            led_ratio = led_index_to_compute / self.led_count
            hour_distance = abs(led_ratio - hour_ratio)
            minute_distance = abs(led_ratio - minute_ratio)
            
            # Graph of LED duty cycle vs distance the LED is to the clock hand
            # when led_count==35
            #
            #   255| \
            # d    |  \
            # u    |   \
            # t    |    \
            # y    |     \
            #      |      \
            # c    |       \
            # y    |        \
            # c    |         \
            # l    |          \
            # e    |           \
            #     0+-----------------
            #      0          (1/35)
            #         distance
            
            rise = -self.max_brightness
            run = 1 / self.led_count
            slope = rise / run
            
            red = max(0, slope * hour_distance + self.max_brightness)
            blue = max(0, slope * minute_distance + self.max_brightness)
            
            green = 0 #5 if (i >= close_blinds_led_index and i <= open_blinds_led_index) else 0
            self.neopixels[led_index_to_set] = (red, green, blue)
            
    def update_time_and_display(self):
            now = datetime.now()
            hour = now.hour
            if hour > 11:
                # Change 24-hour time to 12-hour time.
                # 12 P.M. becomes hour zero, 1 P.M. becomes hour one, etc.
                hour = hour - 12
            minute = now.minute
            second = now.second
            
            #print("hour={:d} minute={:d}".format(hour, minute))
            
            self.display_time(hour, minute, second)
