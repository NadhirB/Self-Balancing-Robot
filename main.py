from MPU6050 import MPU6050
from machine import Pin
from time import sleep
from math import pi

# MPU settings:
mpu = MPU6050()
mpu.set_accel_range(0x10) # can be set to: 0x00 , 0x08 , 0x10 , 0x18
mpu.set_low_pass_filter(0x02) # can be set to: 0x00 , 0x01 ... , 0x06
                              # beware setting too high increases the latency of data


def print_accel_data():
    # Accelerometer Data
    accel = mpu.read_accel_data(g = True)  # read the accelerometer [ms^-2]
    aX = accel["x"]
    aY = accel["y"]
    aZ = accel["z"]
    print(f"ACCEL: x: {aX:+.3f}, y: {aY:+.3f}, z: {aZ:+.3f}")

def print_gyro_data():
    # Gyroscope Data
    gyro = mpu.read_gyro_data()  # read the gyro [deg/s]
    gX = gyro["x"]
    gY = gyro["y"]
    gZ = gyro["z"]
    print(f"GYRO :  x: {gX:+.3f}, y: {gY:+.3f}, z: {gZ:+.3f}")

def print_angle_data():
    # computation of the angle using the accelerometer
    angle = mpu.read_angle()
    angX = angle["x"]
    angX_deg = angX * 180 / pi
    angY = angle["y"]
    angY_deg = angY * 180 / pi
    print(f"Angle X: rad {angX:+.4f} deg {angX_deg:+.5f},  Angle Y: {angY:+.4f} deg {angY_deg:+.5f}")

while True:

    # Time Interval Delay in millisecond (ms)
    sleep(0.1)
