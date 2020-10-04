# -*- coding: utf-8 -*-
from mpu6050 import mpu6050
import gpiozero

class WindowBlinds:
    def __init__(self, guizero_app, direction_pin, pwm_pin):
        self.guizero_app = guizero_app
        
        self.mpu = mpu6050(0x68)
    
        self.accelerometer_Gs_closed = 5.0
        self.accelerometer_Gs_open = 9.7
        
        
        self.direction_device = gpiozero.DigitalOutputDevice(direction_pin)
        
        #textAccel = guizero.Text(guizero_app, text="Z acceleration: ???")
        #def update_accelerometer():
        #    nonlocal latest_accel_z
        #    latest_accel_z = mpu.get_accel_data()["z"]
        #    textAccel.value = "Z acceleration: {:4.2f}".format(latest_accel_z)
        #guizero_app.repeat(100, update_accelerometer)


        pwm_frequency_hz = 20_000
        self.pwm_device = gpiozero.PWMOutputDevice(pwm_pin,  initial_value=0, frequency=pwm_frequency_hz)
    
    def stop(self):
        self.pwm_device.off()
        
    def go_to_open(self):
        self.go_to_accelerometer_Gs(self.accelerometer_Gs_open)
        
    def go_to_closed(self):
        self.go_to_accelerometer_Gs(self.accelerometer_Gs_closed)
        
    def set_cal_open(self):
        gs = get_accelerometer_z_Gs()
        self.accelerometer_Gs_open = gs
        return gs
        
    def set_cal_open(self):
        gs = get_accelerometer_z_Gs()
        self.accelerometer_Gs_closed = gs
        return gs
    
    
    def get_accelerometer_z_Gs(self):
        return self.mpu.get_accel_data()["z"]
    
    def go_to_accelerometer_Gs(self, accelerometer_Gs_target, debug_printouts=False):
        if debug_printouts:
            print("\ngoing to " + str(accelerometer_Gs_target))
        
        accelerometer_Gs_present = self.get_accelerometer_z_Gs()
        if debug_printouts:
            print("   present = {:4.2f}".format(accelerometer_Gs_present))
        
        accelerometer_Gs_difference = accelerometer_Gs_target - accelerometer_Gs_present
        if debug_printouts:
            print("difference = {:4.2f}".format(accelerometer_Gs_difference))
        
        close_enough = 0.05
        if(abs(accelerometer_Gs_difference) < close_enough):
            if debug_printouts:
                print("close enough, returning")
            self.pwm_device.value = 0
            return
            
        self.direction_device.value = 1 if accelerometer_Gs_difference>0 else 0
        
        #pwm_max = 1
        #accel_to_start_slowing_down_at = 1
        #line_slope = 1 / accel_to_start_slowing_down_at
        #new_pwm_value = min(pwm_max, line_slope * abs(difference))
        #print("  new pwm = {:4.2f}".format(new_pwm_value))
        #pwm_device.value = new_pwm_value
        self.pwm_device.value = 1
        self.guizero_app.after(100, self.go_to_accelerometer_Gs, [accelerometer_Gs_target]);
