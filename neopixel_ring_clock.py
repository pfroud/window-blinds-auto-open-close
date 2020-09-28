# -*- coding: utf-8 -*-
from neopixel import NeoPixel
from datetime import datetime

class NeopixelRingClock:
    def __init__(self, pin, led_count, max_brightness, use_smoothing):
         self.neopixels = NeoPixel(pin, led_count)
         self.max_brightness = max_brightness
         self.use_smoothing = use_smoothing
         self.led_count = led_count
         
    def set_max_brightness(self, new_max_brightness):
         self.max_brightness = new_max_brightness
         self.tick()
         
    def update_time(self, hour, minute, second):
        second_ratio = second / 60
        minute_ratio = (minute + second_ratio) / 60
        hour_ratio = (hour + minute_ratio) / 12
        
        hour_led_index = round(self.led_count * hour_ratio)
        minute_led_index = round(self.led_count * minute_ratio)
        
        for i in range(0, self.led_count):
            
            if self.use_smoothing:
                led_ratio = i / self.led_count
                hour_distance = abs(led_ratio - hour_ratio)
                minute_distance = abs(led_ratio - minute_ratio)
                
                rise = self.max_brightness
                run = 1 / self.led_count
                slope = -rise / run
                
                red = max(0, slope * hour_distance + self.max_brightness)
                blue = max(0, slope * minute_distance + self.max_brightness)
                
                
                
            else:
                red = self.max_brightness if i==hour_led_index else 0
                blue = self.max_brightness if i==minute_led_index else 0
               
            green = 0 #5 if (i >= close_blinds_led_index and i <= open_blinds_led_index) else 0
          
            
            self.neopixels[i] = (red, green, blue)
            
    def tick(self):
            now = datetime.now()
            hour = now.hour
            if hour > 11:
                # 12 PM becomes hour zero
                hour = hour - 12
            minute = now.minute
            second = now.second
            #print("hour={:d} minute={:d}".format(hour, minute))
            
            #slider_hour.value = hour
            #slider_minute.value = minute
            #slider_second.value = second
            
            self.update_time(hour, minute, second)
