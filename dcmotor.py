# Created a class object for controlling the dc-motors on the balancing robot
# Bsed on the L298N motor controller
# Written by Nadhir Busheri MAR 2025

# set frequency to

from machine import Pin, PWM

class Motor:

    def __init__(self, pin1, pin2, pin_pwm, frequency: int = 1000, pwm_enable: bool = True , max_speed: int = 1023):

        self.pwm_enable = pwm_enable
        self.max_speed = max_speed

        self.pin1 = Pin(pin1, Pin.OUT)
        self.pin2 = Pin(pin2, Pin.OUT)
        self.pin_pwm = PWM(Pin(pin_pwm), freq = frequency)

    # speed value can be between 0 and 1
    def forward(self, speed):

        self.pin_pwm.duty(self.duty_cycle(speed))
        self.pin1.value(1)
        self.pin2.value(0)
        print(f"forward {self.pin1.value()} {self.pin2.value()}")
    
    
    def backward(self, speed):
        print("backward")
        self.pin_pwm.duty(self.duty_cycle(speed))
        self.pin1.value(0)
        self.pin2.value(1)
    
    
    def stop(self):

        self.pin_pwm.duty(0)
        self.pin1.value(0)
        self.pin2.value(0)

        print(f"stop {self.pin1.value()} {self.pin2.value()}")
    
    
    def duty_cycle(self, speed):
        if speed <= 0 or speed > 1:
            duty_cycle = 0
        elif not self.pwm_enable:
            duty_cycle = self.max_speed
        else:
            duty_cycle = int(speed * self.max_speed)
        return duty_cycle