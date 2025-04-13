# Class to read data from the (GY-521) MPU6050 Accelerometer/Gyro Module
# Ported to MicroPython by Warayut Poomiwatracanont JAN 2023
# His Original repo is https://github.com/Lezgend/MPU6050-MicroPython
# Original repo https://github.com/nickcoutsos/MPU-6050-Python
# and https://github.com/CoreElectronics/CE-PiicoDev-MPU6050-MicroPython-Module
# Added a function to enable the onboard digital Low Pass Filter by Nadhir Busheri MAR 2025
# TODO: add a calibration function

from math import sqrt, atan2, pi
from machine import Pin, SoftI2C
from time import sleep_ms


error_msg = "\nError \n"
i2c_err_str = "ESP32 could not communicate with module at address 0x{:02X}, check wiring"

# Global Variables
_GRAVITY_MS2 = 9.79473

# Scale Modifiers
_ACC_SCLR_2G = 16384.0
_ACC_SCLR_4G = 8192.0
_ACC_SCLR_8G = 4096.0
_ACC_SCLR_16G = 2048.0

_GYR_SCLR_250DEG = 131.0
_GYR_SCLR_500DEG = 65.5
_GYR_SCLR_1000DEG = 32.8
_GYR_SCLR_2000DEG = 16.4

# Pre-defined ranges
_ACC_RNG_2G = 0x00
_ACC_RNG_4G = 0x08
_ACC_RNG_8G = 0x10
_ACC_RNG_16G = 0x18

_GYR_RNG_250DEG = 0x00
_GYR_RNG_500DEG = 0x08
_GYR_RNG_1000DEG = 0x10
_GYR_RNG_2000DEG = 0x18

# MPU-6050 Registers
_PWR_MGMT_1 = 0x6B

_ACCEL_XOUT0 = 0x3B

_TEMP_OUT0 = 0x41

_GYRO_XOUT0 = 0x43

_ACCEL_CONFIG = 0x1C
_GYRO_CONFIG = 0x1B

_DLPF_CONFIG = 0x1A

_maxFails = 3

# Address
_MPU6050_ADDRESS = 0x68

def signedIntFromBytes(x, endian="big"):
    y = int.from_bytes(x, endian)
    if (y >= 0x8000):
        return -((65535 - y) + 1)
    else:
        return y
    

class MPU6050(object):     
    def __init__(self, bus=None, freq=None, sda=None, scl=None, addr = _MPU6050_ADDRESS):
        # Checks any error would happen with I2C communication protocol.
        self._failCount = 0
        self._terminatingFailCount = 0
        
        # Initializing the I2C method for ESP32
        # Pin assignment:
        # SCL -> GPIO 22
        # SDA -> GPIO 21
        self.i2c = SoftI2C(scl=Pin(22), sda=Pin(21), freq=100000)
        
        # Initializing the I2C method for ESP8266
        # Pin assignment:
        # SCL -> GPIO 5
        # SDA -> GPIO 4
        # self.i2c = I2C(scl=Pin(5), sda=Pin(4))
        
        self.addr = addr
        try:
            # Wake up the MPU-6050 since it starts in sleep mode
            self.i2c.writeto_mem(self.addr, _PWR_MGMT_1, bytes([0x00]))
            sleep_ms(5)
        except Exception as e:
            print(i2c_err_str.format(self.addr))
            print(error_msg)
            raise e
        self._accel_range = self.get_accel_range(True)
        self._gyro_range = self.get_gyro_range(True)
        self._gyro_calibration = {"x": 0, "y": 0, "z": 0}

    def _readData(self, register):
        failCount = 0
        while failCount < _maxFails:
            try:
                sleep_ms(10)
                data = self.i2c.readfrom_mem(self.addr, register, 6)
                break
            except:
                failCount = failCount + 1
                self._failCount = self._failCount + 1
                if failCount >= _maxFails:
                    self._terminatingFailCount = self._terminatingFailCount + 1
                    print(i2c_err_str.format(self.addr))
                    return {"x": float("NaN"), "y": float("NaN"), "z": float("NaN")} 
        x = signedIntFromBytes(data[0:2])
        y = signedIntFromBytes(data[2:4])
        z = signedIntFromBytes(data[4:6])
        return {"x": x, "y": y, "z": z}

    def read_temperature(self):
        """
        Reads the temperature from the onboard temperature sensor of the MPU-6050.
        :return: Returns the temperature [degC].
        """
        try:
            rawData = self.i2c.readfrom_mem(self.addr, _TEMP_OUT0, 2)
            raw_temp = (signedIntFromBytes(rawData, "big"))
        except:
            print(i2c_err_str.format(self.addr))
            return float("NaN")
        actual_temp = (raw_temp / 340) + 36.53
        return actual_temp

    def set_accel_range(self, accel_range):
        """
        Sets the range of the accelerometer
        :param accel_range: the range to set the accelerometer to. Using a pre-defined range is advised.
                            can be set to: 0x00 , 0x08 , 0x10 , 0x18
        :return: none
        """
        self.i2c.writeto_mem(self.addr, _ACCEL_CONFIG, bytes([accel_range]))
        self._accel_range = accel_range

    def get_accel_range(self, raw = False):
        """
        Gets the range the accelerometer is set to.
        raw = True: Returns raw value from the ACCEL_CONFIG register
        raw = False: Return integer: -1, 2, 4, 8 or 16. When it returns -1 something went wrong.
        :param raw:
        :return:
        """
        # Get the raw value
        raw_data = self.i2c.readfrom_mem(self.addr, _ACCEL_CONFIG, 2)
        
        if raw is True:
            return raw_data[0]
        elif raw is False:
            if raw_data[0] == _ACC_RNG_2G:
                return 2
            elif raw_data[0] == _ACC_RNG_4G:
                return 4
            elif raw_data[0] == _ACC_RNG_8G:
                return 8
            elif raw_data[0] == _ACC_RNG_16G:
                return 16
            else:
                return -1

    def read_accel_data(self, g = False):
        """
        Reads and returns the AcX, AcY and AcZ values from the accelerometer.

        :param g: sets th data format that is returned g (g = True) or m/s^2 (g = False)
        :return: Returns dictionary data in g or m/s^2
        """
        accel_data = self._readData(_ACCEL_XOUT0)
        accel_range = self._accel_range
        scaler = None
        if accel_range == _ACC_RNG_2G:
            scaler = _ACC_SCLR_2G
        elif accel_range == _ACC_RNG_4G:
            scaler = _ACC_SCLR_4G
        elif accel_range == _ACC_RNG_8G:
            scaler = _ACC_SCLR_8G
        elif accel_range == _ACC_RNG_16G:
            scaler = _ACC_SCLR_16G
        else:
            print("Unknown range - scaler set to _ACC_SCLR_2G")
            scaler = _ACC_SCLR_2G

        x = accel_data["x"] / scaler - 0.038
        y = accel_data["y"] / scaler + 0.019
        z = accel_data["z"] / scaler - 0.069

        if g is True:
            return {"x": x, "y": y, "z": z}
        elif g is False:
            x = x * _GRAVITY_MS2
            y = y * _GRAVITY_MS2
            z = z * _GRAVITY_MS2
            return {"x": x, "y": y, "z": z}

    def read_accel_abs(self, g = False):
        d=self.read_accel_data(g)
        return sqrt(d["x"]**2+d["y"]**2+d["z"]**2)

    def set_gyro_range(self, gyro_range):
        self.i2c.writeto_mem(self.addr, _GYRO_CONFIG, bytes([gyro_range]))
        self._gyro_range = gyro_range


    def get_gyro_range(self, raw = False):
        """
        Gets the range the gyroscope is set to.
        raw = True: return raw value from GYRO_CONFIG register
        raw = False: return range in deg/s
        :param raw:
        :return:
        """
        # Get the raw value
        raw_data = self.i2c.readfrom_mem(self.addr, _GYRO_CONFIG, 2)

        if raw is True:
            return raw_data[0]
        elif raw is False:
            if raw_data[0] == _GYR_RNG_250DEG:
                return 250
            elif raw_data[0] == _GYR_RNG_500DEG:
                return 500
            elif raw_data[0] == _GYR_RNG_1000DEG:
                return 1000
            elif raw_data[0] == _GYR_RNG_2000DEG:
                return 2000
            else:
                return -1

    def read_gyro_data(self):
        """
        Gets and returns the GyX, GyY and GyZ values from the gyroscope.
        :return: Returns the read values in a dictionary.
        """

        gyro_data = self._readData(_GYRO_XOUT0)
        gyro_range = self._gyro_range
        scaler = None
        if gyro_range == _GYR_RNG_250DEG:
            scaler = _GYR_SCLR_250DEG
        elif gyro_range == _GYR_RNG_500DEG:
            scaler = _GYR_SCLR_500DEG
        elif gyro_range == _GYR_RNG_1000DEG:
            scaler = _GYR_SCLR_1000DEG
        elif gyro_range == _GYR_RNG_2000DEG:
            scaler = _GYR_SCLR_2000DEG
        else:
            print("Unknown range - scaler set to _GYR_SCLR_250DEG")
            scaler = _GYR_SCLR_250DEG

        x = gyro_data["x"] / scaler - self._gyro_calibration["x"]
        y = gyro_data["y"] / scaler - self._gyro_calibration["y"]
        z = gyro_data["z"] / scaler - self._gyro_calibration["z"]

        return {"x": x, "y": y, "z": z}

    def read_angle(self, degrees: bool = False):
        """
        returns radians by default, pass degrees = True to get reading in degrees. orientation matches silkscreen

        :param degrees: defines the kind of data that is returned
        :return: The pitch and roll of the MPU6050 in a dictionary format
        """

        a = self.read_accel_data(g = True)
        x = atan2(a["y"],sqrt(a["z"]**2 + a["x"]**2))
        y = atan2(-a["x"],sqrt(a["z"]**2 + a["y"]**2))

        if degrees is True:
            x = x * 180 / pi
            y = y * 180 / pi

        return {"x": x, "y": y}

    def set_low_pass_filter(self, setting):
        """
        Turn on the Low pass filter of the MPU6050
        :param setting: should be between 0x00 and 0x06
        :return: none
        """

        if 0 <= setting <= 6:
            self.i2c.writeto_mem(self.addr, _DLPF_CONFIG, bytes([setting]))
        else:
            self.i2c.writeto_mem(self.addr, _DLPF_CONFIG, bytes([0x00]))
            print("Invalid setting. Must be between 0 and 6, auto set to 0")

    def gyro_calibration(self):
        """
        Calibrates the gyroscope values, should be run every time you start the program
        :return:
        """
        x_cal , y_cal, z_cal = 0.0, 0.0, 0.0
        for n in range(0, 2000):
            gyro_data = self.read_gyro_data()
            x_cal += gyro_data["x"]
            y_cal += gyro_data["y"]
            z_cal += gyro_data["z"]
            n += 1
            sleep_ms(1)

        self._gyro_calibration["x"] = x_cal / 2000
        self._gyro_calibration["y"] = y_cal / 2000
        self._gyro_calibration["z"] = z_cal / 2000

        print("Gyro calibration complete")