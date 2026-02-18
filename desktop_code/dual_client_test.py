import paho.mqtt.client as mqtt
import time

MQTT_BROKER_IP = "192.168.1.85"

# Define Callback for Client A
def on_message_a(client, userdata, message):
    print(f"[Client A] Topic: {message.topic} | Message: {message.payload.decode()}")

# Define Callback for Client B
def on_message_b(client, userdata, message):
    print(f"[Client B] Topic: {message.topic} | Message: {message.payload.decode()}")

# Setup Client A
client_a = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client_a.on_message = on_message_a
client_a.connect(MQTT_BROKER_IP, 1883)
client_a.subscribe("lidar/data")

# Setup Client B
client_b = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client_b.on_message = on_message_b
client_b.connect(MQTT_BROKER_IP, 1883)
client_b.subscribe("odom/pose")

# Start non-blocking loops
client_a.loop_start()
client_b.loop_start()

print("Listening for messages... Press Ctrl+C to stop.")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    client_a.loop_stop()
    client_b.loop_stop()
