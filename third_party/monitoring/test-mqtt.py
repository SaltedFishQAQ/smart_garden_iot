import paho.mqtt.client as mqtt
import json

class MQTTClient:
    def __init__(self, broker, port, topic):
        self.broker = broker
        self.port = port
        self.topic = topic
        self.client = mqtt.Client()

    def connect(self):
        """Connect to the MQTT broker."""
        try:
            self.client.connect(self.broker, self.port)
        except Exception as e:
            print(f"Error connecting to MQTT broker: {e}")

    def publish(self, message):
        """Publish a message to the MQTT broker."""
        try:
            self.client.publish(self.topic, json.dumps(message))
            print(f"Published message: {message}")
        except Exception as e:
            print(f"Error publishing message: {e}")

    def disconnect(self):
        """Disconnect from the MQTT broker."""
        self.client.disconnect()

