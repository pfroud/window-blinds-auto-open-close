# -*- coding: utf-8 -*-
from mpu6050 import mpu6050
from datetime import datetime
import gpiozero
import traceback


class WindowBlinds:
    def __init__(self, guizero_app, h_bridge_pin_1, h_bridge_pin_2, pwm_pin):
        self.guizero_app = guizero_app

        self.accelerometer = mpu6050(0x68)

        self.use_soft_start = False

        # The way my accereometer is oriented:
        #  9.8 m/s on Z axis -->     slat is flat --> blinds open
        # zero m/s on Z axis --> slat is vertical --> blinds closed
        self.accelerometer_Z_meters_per_second_blinds_closed = 5.5
        self.accelerometer_Z_meters_per_second_blinds_open = 9.7

        self.gpio_device_H_bridge_pin_1 = gpiozero.DigitalOutputDevice(
            h_bridge_pin_1)

        self.gpio_device_H_bridge_pin_2 = gpiozero.DigitalOutputDevice(
            h_bridge_pin_2)

        self.gpio_device_motor_speed = gpiozero.PWMOutputDevice(
            pwm_pin, initial_value=0, frequency=20_000)

    def stop(self):
        self.gpio_device_motor_speed.off()

    def go_to_open(self):
        self.go_to_accelerometer_Z_meters_per_second_start(
            self.accelerometer_Z_meters_per_second_blinds_open)

    def go_to_closed(self):
        self.go_to_accelerometer_Z_meters_per_second_start(
            self.accelerometer_Z_meters_per_second_blinds_closed)

    def get_accelerometer_Z_meters_per_second(self):
        return self.accelerometer.get_accel_data()["z"]

    def go_to_accelerometer_Z_meters_per_second_start(
            self, accelerometer_Z_meters_per_second_target):
        self.go_to_accelerometer_Z_meters_per_second(accelerometer_Z_meters_per_second_target,
                                                     None, datetime.now(), self.get_accelerometer_Z_meters_per_second())

    def go_to_accelerometer_Z_meters_per_second(self,
                                                accelerometer_meters_per_second_target,
                                                previous_is_difference_from_target_positive,
                                                initial_datetime,
                                                initial_accelerometer_meters_per_second,
                                                debug_printouts=False):
        try:
            accelerometer_meters_per_second_present = self.get_accelerometer_Z_meters_per_second()
        except OSError:
            # Stop the motor if can't communicate with accelerometer via I2C.
            self.stop()
            traceback.print_exc()
            return

        elapsed_seconds = (datetime.now() - initial_datetime).total_seconds()

        accel_difference_from_initial = initial_accelerometer_meters_per_second - \
            accelerometer_meters_per_second_present

        # Adjust these threshholds through experimentation for how much
        # backlash the window blinds have, and how noisy the acceleroemter is
        if abs(accel_difference_from_initial) < 0.7 and elapsed_seconds > 12:
            self.stop()
            print("Stopping because the accelerometer hasn't moved enough,")
            print("probably forgot to turn on power supply for motor")
            return

        accelerometer_meters_per_second_difference_from_target = accelerometer_meters_per_second_target - \
            accelerometer_meters_per_second_present

        is_difference_from_target_positive = accelerometer_meters_per_second_difference_from_target > 0

        crossed_zero = previous_is_difference_from_target_positive is not None \
            and previous_is_difference_from_target_positive != is_difference_from_target_positive

        is_close_enough = abs(
            accelerometer_meters_per_second_difference_from_target) < 0.05

        if debug_printouts:
            print()
            print(
                f"Accel present = {accelerometer_meters_per_second_present:5.2f} m/s")
            print(f" Elapsed time = {elapsed_seconds:5.2f} seconds")
            print(
                f"Accel initial = {initial_accelerometer_meters_per_second:5.2f} m/s    Difference from present = {accel_difference_from_initial:5.2f} m/s")
            print(
                f" Accel target = { accelerometer_meters_per_second_target:5.2f} m/s    Difference from present = {accelerometer_meters_per_second_difference_from_target:5.2f} m/s")
            print(f"crossed zero? " + str(crossed_zero))
            print(f"close enough? " + str(is_close_enough))

        if crossed_zero or is_close_enough:
            self.stop()
        else:
            if is_difference_from_target_positive:
                self.gpio_device_H_bridge_pin_1.value = 1
                self.gpio_device_H_bridge_pin_2.value = 0
            else:
                self.gpio_device_H_bridge_pin_1.value = 0
                self.gpio_device_H_bridge_pin_2.value = 1

            if(self.use_soft_start):
                time_when_full_speed_starts_seconds = 1
                maximum_speed = 1
                if elapsed_seconds < time_when_full_speed_starts_seconds:
                    self.gpio_device_motor_speed.value = elapsed_seconds / \
                        time_when_full_speed_starts_seconds
                else:
                    self.gpio_device_motor_speed.value = 1
            else:
                self.gpio_device_motor_speed.value = 1

            self.guizero_app.after(
                100, self.go_to_accelerometer_Z_meters_per_second, [
                    accelerometer_meters_per_second_target, is_difference_from_target_positive, initial_datetime, initial_accelerometer_meters_per_second])
