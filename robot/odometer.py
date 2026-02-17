import qwiic_otos
import paho.mqtt.client as mqtt
from math import pi
import time
import json
import sys

# --- MQTT Configuration ---
MQTT_BROKER = "localhost"  # Replace with your MQTT broker address (e.g., "broker.hivemq.com" or a local IP)
MQTT_PORT = 1883           # Default MQTT port
MQTT_TOPIC = "odom/pose"   # The topic to publish data to
MQTT_USERNAME = "robot"
MQTT_PASSWORD = "robot"
client = mqtt.Client()
client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
client.connect(MQTT_BROKER, 1883, 60)


# --- OTOS Configuration ---
# Initialize the SparkFun OTOS
otos = qwiic_otos.QwiicOTOS()
if not otos.is_connected():
    print("The OTOS is not connected. Check wiring.")
    client.loop_stop()
    sys.exit(1)
otos.begin()

# Calibrate the IMU, which removes the accelerometer and gyroscope offsets
print("Ensure the OTOS is flat and stationary during calibration!")
for i in range(5, 0, -1):
    print("Calibrating in %d seconds..." % i)
    time.sleep(1)
print("Calibrating IMU...")
otos.calibrateImu()

# Account for OTOS location w/r/t robot center
offset = qwiic_otos.Pose2D(0, 0, 0)
otos.setOffset(offset)

# Set units for linear and angular measurements.
# If not set, the default is inches and degrees.
# Note that this setting is not stored in the sensor.
# it's part of the library, so you need to set it.
otos.setLinearUnit(otos.kLinearUnitMeters)
otos.setAngularUnit(otos.kAngularUnitRadians)

# Reset the tracking algorithm - this resets the position to the origin,
# but can also be used to recover from some rare tracking errors
otos.resetTracking()
print("OTOS initialized")


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker")
    else:
        print(f"Failed to connect, return code {rc}")

def run_otos_mqtt():
    client.on_connect = on_connect
    
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_start()
    except Exception as e:
        print(f"Could not connect to MQTT broker: {e}")
        sys.exit(1)

    # Main loop to read and publish data
    try:
        while True:
            # Read current pose data (x, y, hdg)
            pose = otos.getPosition()
            pose_data = {
                "x_m": pose.x,
                "y_m": pose.y,
                "hdg_rad": pose.h
            }
            
            # Convert pose data to JSON string
            json_payload = json.dumps(pose_data)
            
            # Publish to MQTT
            result = client.publish(MQTT_TOPIC, json_payload, qos=1)
            status = result[0]
            if status == 0:
                print(f"Sent `{json_payload}` to topic `{MQTT_TOPIC}`")
            else:
                print(f"Failed to send message to topic {MQTT_TOPIC}")

            time.sleep(0.1) # Publish rate of 10 Hz

    except KeyboardInterrupt:
        print("Program terminated by user. Exiting.")
        client.loop_stop()
        client.disconnect()
        sys.exit(0)

if __name__ == "__main__":
    run_otos_mqtt()
