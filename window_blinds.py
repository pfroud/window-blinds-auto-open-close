# -*- coding: utf-8 -*-
from mpu6050 import mpu6050
import gpiozero
import traceback


class WindowBlinds:
    def __init__(self, guizero_app, direction_pin, pwm_pin):
        self.guizero_app = guizero_app

        self.mpu = mpu6050(0x68)

        self.accelerometer_Gs_closed = 6.0
        self.accelerometer_Gs_open = 9.7

        self.direction_device = gpiozero.DigitalOutputDevice(direction_pin)
        self.pwm_device = gpiozero.PWMOutputDevice(
            pwm_pin, initial_value=0, frequency=20_000)

    def stop(self):
        self.pwm_device.off()

    def go_to_open(self):
        self.go_to_accelerometer_Gs(self.accelerometer_Gs_open, None)

    def go_to_closed(self):
        self.go_to_accelerometer_Gs(self.accelerometer_Gs_closed, None)

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

    def go_to_accelerometer_Gs(self, accelerometer_Gs_target,
                               previous_is_difference_positive, debug_printouts=False):
        try:
            accelerometer_Gs_present = self.get_accelerometer_z_Gs()
        except OSError:
            self.stop()
            traceback.print_exc()
            return

        accelerometer_Gs_difference = accelerometer_Gs_target - accelerometer_Gs_present

        is_difference_positive = accelerometer_Gs_difference > 0
        crossed_zero = previous_is_difference_positive is not None and previous_is_difference_positive != is_difference_positive

        is_close_enough = abs(accelerometer_Gs_difference) < 0.05

        if debug_printouts:
            print()
            print(" target Gs = {:5.2f}".format(accelerometer_Gs_target))
            print("present Gs = {:5.2f}".format(accelerometer_Gs_present))
            print("difference = {:5.2f}".format(accelerometer_Gs_difference))
            print("crossed zero? " + str(crossed_zero))
            print("close enough? " + str(is_close_enough))

        if crossed_zero or is_close_enough:
            self.pwm_device.value = 0
        else:
            self.direction_device.value = 1 if is_difference_positive else 0
            self.pwm_device.value = 1
            self.guizero_app.after(
                100, self.go_to_accelerometer_Gs, [
                    accelerometer_Gs_target, is_difference_positive])
