# test for MPU-6050 IMU (accelerometer & gyroscope)
from mpu6050 import mpu6050
import time


def main():
    # When the AD0 pin is low, the I2C address is 0x68.
    # When the AD0 pin is high, the I2C address is 0x69.
    mpu = mpu6050(0x68)

    print("Press Ctrl+C to stop")
    print("|                   |     Acceleration (m/s)   |       Gyroscope (deg/s)     |")
    print("|  Temperature (C)  |     X       Y       Z    |      X        Y        X    |")
    print("|-------------------+--------------------------+-----------------------------|")
    while True:
        try:
            accel_data = mpu.get_accel_data()
            gyro_data = mpu.get_gyro_data()
            print(
                f"\r|       {mpu.get_temp():.1f}        |  {accel_data['x']:+6.2f}  {accel_data['y']:+6.2f}  {accel_data['z']:+6.2f}  |  {gyro_data['x']:+7.2f}  {gyro_data['y']:+7.2f}  {gyro_data['z']:+7.2f}  |",
                end="")
            time.sleep(0.1)
        except KeyboardInterrupt:
            print()
            return


if __name__ == '__main__':
    main()
