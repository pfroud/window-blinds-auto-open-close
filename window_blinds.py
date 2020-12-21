# -*- coding: utf-8 -*-
from mpu6050 import mpu6050
from datetime import datetime
import gpiozero
import traceback


class WindowBlinds:
    def __init__(self, guizero_app, direction_pin, pwm_pin):
        self.guizero_app = guizero_app

        self.accelerometer = mpu6050(0x68)

        # The way my accereometer is oriented:
        #  9.8 Gs on Z axis -->     slat is flat --> blinds open
        # zero Gs on Z axis --> slat is vertical --> blinds closed
        self.accelerometer_z_Gs_blinds_closed = 5.5
        self.accelerometer_z_Gs_blinds_open = 9.7

        self.gpio_device_motor_direction = gpiozero.DigitalOutputDevice(
            direction_pin)
        self.gpio_device_motor_speed = gpiozero.PWMOutputDevice(
            pwm_pin, initial_value=0, frequency=20_000)

    def stop(self):
        self.gpio_device_motor_speed.off()

    def go_to_open(self):
        self.go_to_accelerometer_z_Gs_start(
            self.accelerometer_z_Gs_blinds_open)

    def go_to_closed(self):
        self.go_to_accelerometer_z_Gs_start(
            self.accelerometer_z_Gs_blinds_closed)

    def get_accelerometer_z_Gs(self):
        return self.accelerometer.get_accel_data()["z"]

    def go_to_accelerometer_z_Gs_start(self, accelerometer_z_Gs_target):
        self.go_to_accelerometer_z_Gs(accelerometer_z_Gs_target,
                                      None, datetime.now(), self.get_accelerometer_z_Gs())

    def go_to_accelerometer_z_Gs(self,
                                 accelerometer_Gs_target,
                                 previous_is_difference_from_target_positive,
                                 initial_datetime,
                                 initial_accelerometer_Gs,
                                 debug_printouts=True):
        try:
            accelerometer_Gs_present = self.get_accelerometer_z_Gs()
        except OSError:
            # Stop the motor if can't communicate with accelerometer via I2C.
            self.stop()
            traceback.print_exc()
            return

        elapsed_seconds = (datetime.now() - initial_datetime).total_seconds()
        accel_difference_from_initial = initial_accelerometer_Gs - accelerometer_Gs_present
        # Adjust these threshholds through experimentation for how much
        # backlash the window blinds have, and how noisy the acceleroemter is
        if abs(accel_difference_from_initial) < 0.7 and elapsed_seconds > 8:
            self.stop()
            print("Stopping because the accelerometer hasn't moved enough,")
            print("probably forgot to turn on power supply for motor")
            return

        accelerometer_Gs_difference_from_target = accelerometer_Gs_target - \
            accelerometer_Gs_present
        is_difference_from_target_positive = accelerometer_Gs_difference_from_target > 0
        crossed_zero = previous_is_difference_from_target_positive is not None \
            and previous_is_difference_from_target_positive != is_difference_from_target_positive

        is_close_enough = abs(accelerometer_Gs_difference_from_target) < 0.05

        if debug_printouts:
            print()
            print(f"Accel present = {accelerometer_Gs_present:5.2f} G's")
            print(f" Elapsed time = {elapsed_seconds:5.2f} seconds")
            print(
                f"Accel initial = {initial_accelerometer_Gs:5.2f} G's    Difference from present = {accel_difference_from_initial:5.2f} G's")
            print(
                f" Accel target = { accelerometer_Gs_target:5.2f} G's    Difference from present = {accelerometer_Gs_difference_from_target:5.2f} G's")
            print(f"crossed zero? " + str(crossed_zero))
            print(f"close enough? " + str(is_close_enough))

        if crossed_zero or is_close_enough:
            self.stop()
        else:
            self.gpio_device_motor_direction.value = 1 if is_difference_from_target_positive else 0
            self.gpio_device_motor_speed.value = 1
            self.guizero_app.after(
                100, self.go_to_accelerometer_z_Gs, [
                    accelerometer_Gs_target, is_difference_from_target_positive, initial_datetime, initial_accelerometer_Gs])
