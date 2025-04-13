from MPU6050 import MPU6050
from dcmotor import Motor
from kalman1Dfilter import Kalman1D
from PIDModule import PID
from machine import Pin
from math import pi
from time import sleep, sleep_ms, ticks_ms, ticks_diff


def setup():
    # MPU settings:
    mpu = MPU6050()
    mpu.set_accel_range(0x10)     # can be set to: 0x00 , 0x08 , 0x10 , 0x18
    mpu.set_gyro_range(0x08)      # can be set to: 0x00 , 0x08 , 0x10 , 0x18
    mpu.set_low_pass_filter(0x05) # can be set to: 0x00 , 0x01 ... , 0x06
                                  # beware, setting too high increases the latency of data

    kf_pitch = Kalman1D()
    pid1 = PID(3.2, 0.01, 0.04)

    motor1 = Motor(5, 18, 19, max_speed = 1023)
    motor2 = Motor(17, 16, 4, max_speed = 1023)

    return mpu, kf_pitch, pid1, motor1, motor2


def print_accel_data(mpu):
    # Accelerometer Data
    accel = mpu.read_accel_data(g = True)  # read the accelerometer [ms^-2]
    aX = accel["x"]
    aY = accel["y"]
    aZ = accel["z"]
    print(f"ACCEL: x: {aX:+.3f}, y: {aY:+.3f}, z: {aZ:+.3f}")

def print_gyro_data(mpu):
    # Gyroscope Data
    gyro = mpu.read_gyro_data()  # read the gyro [deg/s]
    gX = gyro["x"]
    gY = gyro["y"]
    gZ = gyro["z"]
    print(f"GYRO :  x: {gX:+.3f}, y: {gY:+.3f}, z: {gZ:+.3f}")

def print_angle_data(mpu):
    # computation of the angle using the accelerometer
    angle = mpu.read_angle()
    angX = angle["x"]
    angX_deg = angX * 180 / pi
    angY = angle["y"]
    angY_deg = angY * 180 / pi
    print(f"Angle X: rad {angX:+.4f} deg {angX_deg:+.5f},  Angle Y: {angY:+.4f} deg {angY_deg:+.5f}")

def get_angles(mpu, kf_pitch, dt):
    angle = mpu.read_angle(degrees = True)
    gyro = mpu.read_gyro_data()    # in deg/s

    ang_y = angle["y"]

    gy = gyro["y"]

    # Update Kalman filters
    pitch = kf_pitch.update(gy, ang_y, dt)

    return pitch

def motor_control(motor1, motor2, pid_in, angle):
    # Clamp PID output to expected range
    min_out, max_out = -300, 300
    pid_output = max(min(abs(pid_in), max_out), min_out)

    # Normalize to 0.0 - 1.0 range
    norm = (pid_output - min_out) / (max_out - min_out)

    # Scale to power range
    min_power, max_power = 0.0, 1.0
    amount = min_power + norm * (max_power - min_power)

    if pid_in < 0:
        motor1.forward(amount)
        motor2.forward(amount)
    elif pid_in >= 0:
        motor1.backward(amount)
        motor2.backward(amount)
    # else:
    #     motor1.stop()
    #     motor2.stop()


def main():

    mpu, kf_pitch, pid1, motor1, motor2 = setup()
    prev = ticks_ms()
    desired_angle = 0

    while True:
        now = ticks_ms()
        dt = ticks_diff(now, prev) / 1000  # in seconds
        prev = now

        measured_angel = get_angles(mpu, kf_pitch, dt)
        #print_accel_data(mpu)
        #gyro_data = mpu.read_gyro_data()
        print(f"Angle {measured_angel}")

        pid1_out = pid1.compute_pid(desired_angle, measured_angel, dt)
        print(f"PID output {pid1_out}")

        motor_control(motor1, motor2, pid1_out, measured_angel)


if __name__ == '__main__':
    main()