import paho.mqtt.client as mqtt
import time

# MQTT Broker Details (using a public test broker)
BROKER_ADDRESS = "mqtt.eclipseprojects.io" #
PORT = 1883
TOPICS = [("test/topic1", 0), ("test/topic2", 0)] # List of (topic, qos) tuples

# The callback for when the client receives a CONNACK response from the broker.
def on_connect(client, userdata, flags, rc):
    """Subscribes to the topics once connected to the broker."""
    if rc == 0:
        print("Connected to MQTT Broker!")
        # Subscribe to multiple topics in one go
        client.subscribe(TOPICS) 
    else:
        print(f"Failed to connect, return code {rc}")

# The callback for when a message is received from the broker.
def on_message(client, userdata, msg):
    """Handles incoming messages and identifies their topic."""
    # The `msg.topic` attribute indicates which topic the message came from
    print(f"Received message on topic '{msg.topic}': {msg.payload.decode()}")

def main():
    # Create an MQTT client instance
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1) # Using VERSION1 API for this example
    client.on_connect = on_connect
    client.on_message = on_message

    # Connect to the broker
    try:
        client.connect(BROKER_ADDRESS, PORT, 60)
    except Exception as e:
        print(f"Connection failed: {e}")
        return

    # Start the network loop in a background thread
    # This allows the script to run and process incoming messages
    client.loop_start()

    try:
        # Keep the script running to receive messages
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        # Gracefully disconnect on keyboard interrupt
        print("Exiting and disconnecting...")
        client.disconnect()
        client.loop_stop()

if __name__ == "__main__":
    main()
