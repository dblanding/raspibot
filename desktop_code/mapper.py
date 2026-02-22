import asyncio
import aiomqtt
import json
import numpy as np
import sys
import time
from build_ogm import Build_OGM
import parameters

class MQTTSubscriber:
    def __init__(self, broker, port, topics):
        self.broker = broker
        self.port = port
        self.topics = topics
        # Dictionary to store the latest message for each topic
        self.latest_messages = {topic: None for topic in topics}
        self.client = None

    async def connect_and_subscribe(self):
        """Connects to the broker and starts the subscription loop."""
        # Use a context manager for reliable connection/disconnection
        try:
            async with aiomqtt.Client(hostname=self.broker, port=self.port) as client:
                self.client = client
                # Subscribe to all topics in the list
                for topic in self.topics:
                    await client.subscribe(topic)
                    print(f"Subscribed to topic: {topic}")
                
                # Start the message listener
                await self.message_listener()
        except aiomqtt.MqttError as e:
            print(f"MQTT error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    async def message_listener(self):
        """Asynchronously listens for and processes incoming messages."""
        async for message in self.client.messages:
            topic = message.topic.value
            payload = message.payload.decode('utf-8')
            # Update the latest message in the dictionary
            self.latest_messages[topic] = payload
            if parameters.debug:
                print(f"Received on '{topic}' @ {time.monotonic()} sec.")

    def get_latest_messages(self):
        """Retrieves the latest messages stored in the dictionary."""
        return self.latest_messages


async def main(ogm):
    
    broker_address = "192.168.1.85"
    mqtt_topics = ["lidar/data", "odom/pose"]
    
    subscriber = MQTTSubscriber(broker_address, 1883, mqtt_topics)
    pose = None
    scan = None
    
    # Run the connection and subscription in an asyncio task
    # Note: This will run forever until stopped
    listener_task = asyncio.create_task(subscriber.connect_and_subscribe())

    # Example of how to retrieve the messages periodically
    # We'll update the map once per second for n seconds
    await asyncio.sleep(5) 
    print("start driving")
    for i in range(1, parameters.n + 1):
        await asyncio.sleep(1)
        print(f"{i} seconds")
        current_messages = subscriber.get_latest_messages()
        for topic, message in current_messages.items():
            if topic == "lidar/data":
                if message:
                    scan = json.loads(message)
                    print(f"scan len: {len(scan)}")
            elif topic == "odom/pose":
                if message:
                    pose = json.loads(message)
                    print(f"pose: {pose}")

            # Update map
            if pose and scan:
                start_time = time.monotonic()
                ogm.update_map(pose, scan)
                end_time = time.monotonic()
                if parameters.debug:
                    elapsed = end_time - start_time
                    print(f"Execution time for update: {elapsed} sec.")

    # The listener_task is still running. In a real app (e.g., web server)
    # the main program would continue to run without blocking.
    # To keep the script running indefinitely to receive messages, you would
    # typically just await the listener task forever. ctrl-c to stop.
    await listener_task

if __name__ == "__main__":
    # Initialize OGM
    ogm = Build_OGM(width=parameters.width,
                    height=parameters.height,
                    resolution=parameters.resolution,
                    orig_x_pos=parameters.orig_x_pos,
                    orig_y_pos=parameters.orig_y_pos)
    try:
        asyncio.run(main(ogm))
    except KeyboardInterrupt:
        print("Subscriber stopped manually.")
    finally:
        # save the map
        np.save('my_map.npy', ogm.data)
        print("Map saved to my_map.npy")
