import paho.mqtt.client as mqtt

# --- Configuration ---
MQTT_BROKER_IP = "192.168.1.85"
MQTT_PORT = 1883
MQTT_TOPIC = "lidar/data"
USERNAME = "robot"
PASSWORD = "robot"
# ---------------------

def on_connect(client, userdata, flags, rc):
    """The callback for when the client connects to the broker."""
    if rc == 0:
        print("Connected to MQTT Broker!")
        client.subscribe(MQTT_TOPIC)
    else:
        print(f"Failed to connect, return code {rc}")

def on_message(client, userdata, msg):
    """The callback for when a PUBLISH message is received from the server."""
    print(f"Received message on topic {msg.topic}: {msg.payload.decode('utf-8')}")

def main():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
    client.on_connect = on_connect
    client.on_message = on_message
    client.username_pw_set(USERNAME, PASSWORD)

    try:
        client.connect(MQTT_BROKER_IP, MQTT_PORT, 60)
    except Exception as e:
        print(f"Connection failed: {e}")
        return

    client.loop_forever()

if __name__ == "__main__":
    main()
