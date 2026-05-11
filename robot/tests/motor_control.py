#!/usr/bin/env python3
"""
motor_control_service.py - MQTT subscriber for motor commands
Runs on RASPBERRY PI as a service
Subscribes to: Topics.MOTOR_CMD
"""
import paho.mqtt.client as mqtt
import serial
import json
import time
import sys
sys.path.insert(0, '..')  # path to where topics.py is
from topics import Topics




class MotorControl:
    """
    MQTT to Serial bridge for motor control
    """
    
    def __init__(self, serial_port='/dev/serial0', baudrate=115200):
        # Serial connection to motor controller
        print(f"🔌 Connecting to serial port {serial_port}...")
        try:
            self.ser = serial.Serial(serial_port, baudrate, timeout=1)
            time.sleep(0.1)
            print(f"✅ Serial connected")
        except Exception as e:
            print(f"❌ Serial connection failed: {e}")
            sys.exit(1)

        # MQTT client
        print(f"🔌 Connecting to MQTT broker (localhost)...")
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        
        try:
            self.client.connect('localhost', 1883, 60)
            print(f"✅ MQTT connected")
        except Exception as e:
            print(f"❌ MQTT connection failed: {e}")
            sys.exit(1)

        print(f"\n{'='*60}")
        print(f"🤖 Motor Control Service Ready")
        print(f"{'='*60}")
        print(f"Subscribed to:")
        print(f"  - {Topics.MOTOR_CMD} (velocity commands)")
        print(f"{'='*60}\n")

        # SET TO AUTO MODE ON STARTUP
        self.set_mode("AUTO")
        time.sleep(0.1)
        
        # Start MQTT loop
        try:
            self.client.loop_forever()
        except Exception as e:
            self.stop()
            self.set_mode("TELEOP")
    
    def on_connect(self, client, userdata, flags, rc):
        """MQTT connection callback"""
        if rc == 0:
            # Subscribe to motor commands
            client.subscribe(Topics.MOTOR_CMD)
        else:
            print(f"❌ MQTT connection failed with code {rc}")
            sys.exit(1)
    
    def on_message(self, client, userdata, msg):
        """MQTT message callback"""
        try:
            # Parse JSON payload
            data = json.loads(msg.payload.decode())
            
            # Handle motor command messages
            if msg.topic == Topics.MOTOR_CMD:
                # Extract velocity commands
                linear = float(data.get('linear', 0.0))
                angular = float(data.get('angular', 0.0))
                
                # Format serial command: V,linear,angular
                cmd = f"V,{linear:.3f},{angular:.3f}\n"
                
                # Send to motor controller
                self.ser.write(cmd.encode())
                
                # Optional: print received commands (comment out for less verbose output)
                print(f"📤 v={linear:6.3f} m/s, ω={angular:6.3f} rad/s")
        
        except Exception as e:
            self.stop()
            self.set_mode("TELEOP")
            print(f"⚠️  Error processing message: {e}")
            print(f"    Topic: {msg.topic}")
            print(f"    Payload: {msg.payload.decode()}")

    def set_mode(self, mode):
        """Set mode: AUTO or TELEOP"""
        cmd = f"M,{mode}\n"
        print(f"Sending: {cmd.strip()}")
        self.ser.write(cmd.encode())
    
    def set_velocity(self, linear, angular):
        """
        Set velocity command.
        linear: m/s (positive = forward)
        angular: rad/s (positive = counter-clockwise)
        """
        cmd = f"V,{linear:.3f},{angular:.3f}\n"
        print(f"Sending: {cmd.strip()}")
        self.ser.write(cmd.encode())
    
    def stop(self):
        """Emergency stop"""
        cmd = "S\n"
        print(f"Sending: {cmd.strip()}")
        self.ser.write(cmd.encode())
    
if __name__ == "__main__":
    mc = MotorControl()
