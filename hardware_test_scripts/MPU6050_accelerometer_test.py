# test for MPU-6050 IMU (accelerometer & gyroscope)
from mpu6050 import mpu6050


def main():
    # When the AD0 pin is low, the I2C address is 0x68.
    # When the AD0 pin is high, the I2C address is 0x69.
    mpu = mpu6050(0x68)

    print("teperature = ", mpu.get_temp(), " C")

    accel_data = mpu.get_accel_data()
    print("acceleration x = ", accel_data['x'])
    print("acceleration y = ", accel_data['y'])
    print("acceleration z = ", accel_data['z'])

    gyro_data = mpu.get_gyro_data()
    print("gyroscope x = ", gyro_data['x'])
    print("gyroscope y = ", gyro_data['y'])
    print("gyroscope z = ", gyro_data['z'])

if __name__ == '__main__':
    main()
