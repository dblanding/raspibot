# diff-drive.py (aka main.py)
"""
Async microPython code to tele-op differetial drive
car using a 2-axis joystick communicating via BLE
*************************************************
FPV: Car goes in direction joystick is pushed.
"""

import aioble
import asyncio
import bluetooth
import struct
import time
from machine import Pin
from mtr import mtr1, mtr3

# Setup onboard LED
led = Pin("LED", Pin.OUT, value=0)

###################################
#
# Bluetooth
#
###################################

# BLE values
ble_name = "3axis_joystk"
ble_svc_uuid = bluetooth.UUID(0x1812)
ble_characteristic_uuid = bluetooth.UUID(0x2A4D)
ble_scan_length = 5000
ble_interval = 30000
ble_window = 30000

async def ble_scan():
    print("Scanning for BLE beacon named", ble_name, "...")
    async with aioble.scan(
    ble_scan_length,
    interval_us=ble_interval,
    window_us=ble_window,
    active=True) as scanner:
        async for result in scanner:
            if result.name() == ble_name and \
               ble_svc_uuid in result.services():
                return result.device
    return None

def decode(data):
    """Unpack X, Y, Z joystick values from BLE data"""
    return struct.unpack("3i", data)


async def main():
    while True:
        device = await ble_scan()
        if not device:
            print("BLE beacon not found.")
            continue

        try:
            print("Connecting to", device)
            connection = await device.connect()
        except asyncio.TimeoutError:
            print("Connection timed out.")
            continue

        async with connection:
            try:
                ble_service = await connection.service(ble_svc_uuid)
                ble_characteristic = await \
                  ble_service.characteristic(ble_characteristic_uuid)
            except (asyncio.TimeoutError, AttributeError):
                print("Timeout discovering services/characteristics.")
                continue

            while True:
                try:
                    js_vals = decode(await ble_characteristic.read())
                    print(f"Joystick Values: {js_vals}")
                    x, y, z = js_vals
                    
                    # scale values by 100/127
                    x = int(x * 100/127)
                    y = int(y * 100/127)
                    
                    # combine joystick values to get raw spd for motors
                    s1 = int(y + x/2)
                    s3 = int(y - x/2)
                    
                    # only allow values between -100 and +100
                    if s1 > 100:
                        s1 = 100
                    if s1 < -100:
                        s1 = -100
                    if s3 > 100:
                        s3 = 100
                    if s3 < -100:
                        s3 = -100
                    
                    # Drive the motors
                    mtr3.drive(s3)
                    mtr1.drive(s1)
                    
                    led.toggle()
                    await asyncio.sleep(0.1)
                except Exception as e:
                    print(f"Error: {e}")
                    continue

asyncio.run(main())
