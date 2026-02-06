"""
This library is used for speed control of 4 motors
attached to the Waveshare Pico Motor Driver Board.

Usage:
from mtr import mtr1, mtr2, mtr3, mtr4

mtr1.drive(spd1)
mtr2.drive(spd2)
mtr3.drive(spd3)
mtr4.drive(spd4)

mtr1.stop()
mtr2.stop()
mtr3.stop()
mtr4.stop()

# spd values are within +/-100
# Max spd fwd = +100
# Max spd rev = -100
"""

import time
from machine import Pin, I2C
import math

class PCA9685:
    # Registers/etc.
    __SUBADR1            = 0x02
    __SUBADR2            = 0x03
    __SUBADR3            = 0x04
    __MODE1              = 0x00
    __PRESCALE           = 0xFE
    __LED0_ON_L          = 0x06
    __LED0_ON_H          = 0x07
    __LED0_OFF_L         = 0x08
    __LED0_OFF_H         = 0x09
    __ALLLED_ON_L        = 0xFA
    __ALLLED_ON_H        = 0xFB
    __ALLLED_OFF_L       = 0xFC
    __ALLLED_OFF_H       = 0xFD

    def __init__(self, address=0x40, debug=False):
        self.i2c = I2C(0, scl=Pin(21), sda=Pin(20), freq=100000)
        self.address = address
        self.debug = debug
        if (self.debug):
            print("Reseting PCA9685") 
        self.write(self.__MODE1, 0x00)
	
    def write(self, cmd, value):
        "Writes an 8-bit value to the specified register/address"
        self.i2c.writeto_mem(int(self.address), int(cmd), bytes([int(value)]))
        if (self.debug):
            print("I2C: Write 0x%02X to register 0x%02X" % (value, cmd))
	  
    def read(self, reg):
        "Read an unsigned byte from the I2C device"
        rdate = self.i2c.readfrom_mem(int(self.address), int(reg), 1)
        if (self.debug):
            print("I2C: Device 0x%02X returned 0x%02X from reg 0x%02X" % (self.address, int(reg), rdate[0]))
        return rdate[0]
	
    def setPWMFreq(self, freq):
        "Sets the PWM frequency"
        prescaleval = 25000000.0    # 25MHz
        prescaleval /= 4096.0       # 12-bit
        prescaleval /= float(freq)
        prescaleval -= 1.0
        if (self.debug):
            print("Setting PWM frequency to %d Hz" % freq)
            print("Estimated pre-scale: %d" % prescaleval)
        prescale = math.floor(prescaleval + 0.5)
        if (self.debug):
            print("Final pre-scale: %d" % prescale)

        oldmode = self.read(self.__MODE1)
        #print("oldmode = 0x%02X" %oldmode)
        newmode = (oldmode & 0x7F) | 0x10        # sleep
        self.write(self.__MODE1, newmode)        # go to sleep
        self.write(self.__PRESCALE, int(math.floor(prescale)))
        self.write(self.__MODE1, oldmode)
        time.sleep(0.005)
        self.write(self.__MODE1, oldmode | 0x80)

    def setPWM(self, channel, on, off):
        "Sets a single PWM channel"
        self.write(self.__LED0_ON_L+4*channel, on & 0xFF)
        self.write(self.__LED0_ON_H+4*channel, on >> 8)
        self.write(self.__LED0_OFF_L+4*channel, off & 0xFF)
        self.write(self.__LED0_OFF_H+4*channel, off >> 8)
        if (self.debug):
            print("channel: %d  LED_ON: %d LED_OFF: %d" % (channel,on,off))
	  
    def setServoPulse(self, channel, pulse):
        pulse = pulse * (4095 / 100)
        self.setPWM(channel, 0, int(pulse))
    
    def setLevel(self, channel, value):
        if (value == 1):
              self.setPWM(channel, 0, 4095)
        else:
              self.setPWM(channel, 0, 0)

class Motor():
    def __init__(self, spd_pin, d1_pin, d2_pin):
        """
        Here are the allowable arguments:
        0, 1, 2
        3, 4, 5
        6, 7, 8
        9, 10, 11
        """
        self.pwm = PCA9685()
        self.pwm.setPWMFreq(50)
        self.spd_pin = spd_pin
        self.d1_pin = d1_pin
        self.d2_pin = d2_pin

    def forward(self, speed):
        """Accepts only pos values of speed"""
        self.pwm.setLevel(self.d1_pin, 1)
        self.pwm.setLevel(self.d2_pin, 0)
        self.pwm.setServoPulse(self.spd_pin, speed)        
        

    def backward(self, speed):
        """Accepts only pos values of speed"""
        self.pwm.setLevel(self.d1_pin, 0)
        self.pwm.setLevel(self.d2_pin, 1)
        self.pwm.setServoPulse(self.spd_pin, speed)        
        

    def stop(self):
        self.pwm.setServoPulse(self.spd_pin, 0)        
        self.pwm.setLevel(self.d1_pin, 0)
        self.pwm.setLevel(self.d2_pin, 0)

    def drive(self, speed):
        """Accepts both pos & neg values of speed"""
        print(f"Speed = {speed}")
        if speed < 0:
            self.backward(-speed)
        else:
            self.forward(speed)


mtr1 = Motor(0, 1, 2)
mtr2 = Motor(3, 4, 5)
mtr3 = Motor(6, 7, 8)
mtr4 = Motor(9, 10, 11)

if __name__ == '__main__':
    print("Drive fwd")
    mtr1.drive(100)
    mtr2.drive(100)
    mtr3.drive(100)
    mtr4.drive(100)
    time.sleep(1)
    print("Stop")
    mtr1.stop()
    mtr2.stop()
    mtr3.stop()
    mtr4.stop()
    time.sleep(1)
    print("Drive rev")
    mtr1.drive(-80)
    mtr2.drive(-80)
    mtr3.drive(-80)
    mtr4.drive(-80)
    time.sleep(1)
    print("Stop")
    mtr1.stop()
    mtr2.stop()
    mtr3.stop()
    mtr4.stop()

    
