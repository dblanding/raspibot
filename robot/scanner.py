import paho.mqtt.client as mqtt
import json
import RPi.GPIO as GPIO
from rplidar import RPLidar
import time

INPUT_PIN = 17 # GPIO pin 17 (Physical pin 11)
GPIO.setmode(GPIO.BCM)
GPIO.setup(INPUT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# MQTT Setup
broker = "localhost"
topic = "lidar/data"
mqtt_username = "robot"
mqtt_password = "robot"
client = mqtt.Client()
client.username_pw_set(mqtt_username, mqtt_password)
client.connect(broker, 1883, 60)

# Create a Lidar object
lidar = RPLidar('/dev/ttyUSB0')

info = lidar.get_info()
print(f"info: {info}")

health = lidar.get_health()
print(f"health: {health}")

def run():
    print('Starting scan...')
    # Iterate over scans (motor runs automatically when scanning starts)
    for scan in lidar.iter_scans():
        data = []
        for (_, angle, distance) in scan:
            data.append({"a": round(angle, 2), "d": round(distance, 2)})

        # Publish
        payload = json.dumps(data)
        client.publish(topic, payload)
        
        if not GPIO.input(INPUT_PIN) == GPIO.LOW:
            break
        time.sleep(0.06)

    # Stop the motor and disconnect cleanly
    print('Stopping motor and disconnecting...')
    lidar.stop()           # Stops the scanning/data acquisition
    lidar.stop_motor()     # Explicitly stops the motor
    print('RPLidar stopped.')

def stop():
    lidar.stop()
    lidar.stop_motor()

if __name__ == '__main__':
    try:
        while True:
            while GPIO.input(INPUT_PIN) == GPIO.LOW:
                run()
            stop()
            time.sleep(1)

    except KeyboardInterrupt:
        print('Interrupted by user, stopping...')

    finally:
        # Stop the motor and disconnect cleanly
        print('Stopping motor and disconnecting...')
        lidar.stop()           # Stops the scanning/data acquisition
        lidar.stop_motor()     # Explicitly stops the motor
        lidar.disconnect()     # Disconnects from the serial port
        client.disconnect()
        print('RPLidar stopped and disconnected.')
