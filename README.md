# Self-Balancing Robot with ESP32 (MicroPython)

## Description
A small yet powerful self-balancing robot project built using an ESP32 microcontroller and programmed in MicroPython. It uses real-time sensor data and PID control to maintain balance on two wheels.
The project started as a way to improve my coding skills and learn new things, it was alot of fun and I'm hoping to do more projects like it.

## Demo

<p align="center">
  <img src="Videos/demo.gif" alt="Self-Balancing Robot Demo" width="30%">
</p>

## Features
- Real-time self-balancing
- Lightweight MicroPython firmware
- Modular, easy-to-extend codebase

## Hardware Used
- ESP32 Development Board
- MPU6050 (or compatible) IMU Sensor
- DC Motors with Motor Driver (L298N or similar)
- Battery Pack (Li-Ion or similar) I used a 9V battery
- Chassis and wheels

## Software Used
- MicroPython Firmware for ESP32
- Libraries:
  - `machine`
  - `time`
  - `math`
- Modules written specifically for the project:
  - `MPU6050`
  - `PIDModule`
  - `dcmotor`
  - `kalman1Dfilter`


## Setup Instructions

### 1. Flash MicroPython Firmware
- Download [MicroPython firmware for ESP32](https://micropython.org/download/esp32/).
- Flash using [esptool.py](https://github.com/espressif/esptool).

### 2. Upload Code
- Clone this repository.
- Use [Thonny](https://thonny.org) or an FTP client to upload the code.
- Make sure to update the pin numbers according to the connections you'll make between the various parts.

### 3. Wiring Connections
- Connect MPU6050 to ESP32 via I2C (SCL/SDA).
- Connect motors to motor driver and motor driver to ESP32.
- Make sure to change the pin numbers in the software so it corresponds to the pins you chose.

## How It Works
- The MPU6050 sensor provides real-time angle measurements (pitch/roll).
- The data is passed through a Kalman Filter for stable values
- A PID controller computes the correction needed based on tilt angle.
- The motor driver adjusts motor speed and direction to maintain balance.


## Usage
- Power on the robot.
- ESP32 will automatically initiate balancing.
- Adjust PID values for optimal performance if needed.

## Future Improvements
- Add remote control via Wi-Fi or Bluetooth
- Integrate a web-based dashboard for monitoring
- Add obstacle detection (e.g., ultrasonic sensor)

## License
Licensed under the [MIT License](LICENSE).

## Credits
- [MicroPython](https://micropython.org/)
- [MPU6050 module written by Warayut](https://github.com/Lezgend/MPU6050-MicroPython/tree/main)
- [Carbon Aeronautics](https://github.com/CarbonAeronautics?tab=repositories)

---
