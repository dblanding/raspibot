# main.py
"""
Async microPython code to tele-op differential drive
car using a 2-axis joystick communicating via BLE
with UART override from Raspberry Pi
*************************************************
FPV: Car goes in direction joystick is pushed.
Priority: BLE joystick > Pi UART commands
"""

import aioble
import asyncio
import bluetooth
import struct
import time
from machine import Pin, UART
from mtr import mtr1, mtr3

# Setup onboard LED
led = Pin("LED", Pin.OUT, value=0)

# Setup UART for Raspberry Pi communication
uart = UART(0, baudrate=115200, tx=Pin(0), rx=Pin(1))

# Robot parameters (measure and adjust these)
WHEEL_SEPARATION = 0.19  # meters - distance between left and right wheels
MAX_SPEED_MPS = 0.32     # meters per second - calibrate this

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

###################################
#
# UART Command Processing
#
###################################

class UARTCommander:
    def __init__(self):
        self.mode = "TELEOP"
        self.last_linear = 0.0
        self.last_angular = 0.0
        
    def velocity_to_motor_command(self, wheel_velocity_mps):
        """Convert wheel velocity (m/s) to motor command (-100 to 100)"""
        motor_command = (wheel_velocity_mps / MAX_SPEED_MPS) * 100
        return int(max(-100, min(100, motor_command)))
    
    def set_velocity(self, linear_vel, angular_vel):
        """
        Convert velocity commands to motor speeds using differential drive kinematics.
        Returns (left_speed, right_speed) as integers -100 to 100
        """
        # Differential drive kinematics
        left_vel_mps = linear_vel - (angular_vel * WHEEL_SEPARATION / 2)
        right_vel_mps = linear_vel + (angular_vel * WHEEL_SEPARATION / 2)
        
        # Convert m/s to motor command (-100 to 100)
        left_speed = self.velocity_to_motor_command(left_vel_mps)
        right_speed = self.velocity_to_motor_command(right_vel_mps)
        
        return left_speed, right_speed
    
    def parse_command(self, cmd_str):
        """
        Parse UART command string.
        Returns dict with command info or None
        """
        try:
            cmd = cmd_str.strip()
            
            if cmd.startswith("V,"):
                # Velocity command: V,linear,angular
                parts = cmd.split(",")
                linear = float(parts[1])
                angular = float(parts[2])
                self.last_linear = linear
                self.last_angular = angular
                return {
                    'type': 'VELOCITY',
                    'linear': linear,
                    'angular': angular
                }
            elif cmd.startswith("M,"):
                # Mode command: M,AUTO or M,TELEOP
                self.mode = cmd.split(",")[1]
                print(f"Mode: {self.mode}")
                return {
                    'type': 'MODE',
                    'mode': self.mode
                }
            elif cmd == "S":
                # Stop command
                self.last_linear = 0.0
                self.last_angular = 0.0
                return {'type': 'STOP'}
        except Exception as e:
            print(f"Parse error: {e}")
        return None

uart_cmd = UARTCommander()

async def uart_reader():
    """Background task to read UART commands"""
    buffer = ""
    while True:
        if uart.any():
            try:
                data = uart.read()
                if data:
                    buffer += data.decode('utf-8', 'ignore')
                    # Process complete lines
                    while '\n' in buffer:
                        line, buffer = buffer.split('\n', 1)
                        cmd = uart_cmd.parse_command(line)
                        if cmd:
                            print(f"Pi cmd: {cmd}")
            except Exception as e:
                print(f"UART error: {e}")
        await asyncio.sleep(0.01)  # Check UART every 10ms

###################################
#
# Motor Control
#
###################################

async def motor_controller(ble_active, js_vals_shared):
    """
    Background task to control motors.
    Priority: BLE joystick > Pi commands
    """
    last_ble_time = time.ticks_ms()
    ble_timeout_ms = 500  # Switch to AUTO after 500ms of no BLE
    
    while True:
        try:
            # Check if we have recent BLE input
            if ble_active[0]:
                last_ble_time = time.ticks_ms()
                x, y = js_vals_shared[0], js_vals_shared[1]
                
                # Scale values by 100/127
                x = int(x * 100/127)
                y = int(y * 100/127)
                
                # Combine joystick values to get raw speed for motors
                s1 = int(y + x/2)
                s3 = int(y - x/2)
                
                # Clamp values between -100 and +100
                s1 = max(-100, min(100, s1))
                s3 = max(-100, min(100, s3))
                
                # Drive the motors
                mtr1.drive(s1)
                mtr3.drive(s3)
                
            elif time.ticks_diff(time.ticks_ms(), last_ble_time) > ble_timeout_ms:
                # No recent BLE input
                if uart_cmd.mode == "AUTO":
                    # Use Pi velocity commands
                    s1, s3 = uart_cmd.set_velocity(
                        uart_cmd.last_linear,
                        uart_cmd.last_angular
                    )
                    mtr1.drive(s1)
                    mtr3.drive(s3)
                else:
                    # TELEOP mode but no joystick - stop
                    mtr1.stop()
                    mtr3.stop()
            
            await asyncio.sleep(0.02)  # 50 Hz motor update
            
        except Exception as e:
            print(f"Motor controller error: {e}")
            mtr1.stop()
            mtr3.stop()
            await asyncio.sleep(0.1)

###################################
#
# Main Loop
#
###################################

async def ble_handler(ble_active, js_vals_shared):
    """Handle BLE connection and joystick reading"""
    while True:
        device = await ble_scan()
        if not device:
            print("BLE beacon not found.")
            ble_active[0] = False
            await asyncio.sleep(1)
            continue

        try:
            print("Connecting to", device)
            connection = await device.connect()
        except asyncio.TimeoutError:
            print("Connection timed out.")
            ble_active[0] = False
            continue

        async with connection:
            try:
                ble_service = await connection.service(ble_svc_uuid)
                ble_characteristic = await \
                  ble_service.characteristic(ble_characteristic_uuid)
            except (asyncio.TimeoutError, AttributeError):
                print("Timeout discovering services/characteristics.")
                ble_active[0] = False
                continue

            print("BLE connected")
            while True:
                try:
                    js_vals = decode(await ble_characteristic.read())
                    x, y, z = js_vals
                    
                    # Update shared values
                    js_vals_shared[0] = x
                    js_vals_shared[1] = y
                    js_vals_shared[2] = z
                    ble_active[0] = True
                    
                    led.toggle()
                    await asyncio.sleep(0.1)
                    
                except Exception as e:
                    print(f"BLE read error: {e}")
                    ble_active[0] = False
                    break

async def main():
    # Shared state between tasks
    ble_active = [False]  # Use list so it's mutable across tasks
    js_vals_shared = [0, 0, 0]  # [x, y, z]
    
    # Create all tasks
    tasks = [
        asyncio.create_task(ble_handler(ble_active, js_vals_shared)),
        asyncio.create_task(motor_controller(ble_active, js_vals_shared)),
        asyncio.create_task(uart_reader())
    ]
    
    # Run all tasks concurrently
    await asyncio.gather(*tasks)

print("Starting robot controller...")
print("BLE joystick has priority over Pi commands")
asyncio.run(main())
