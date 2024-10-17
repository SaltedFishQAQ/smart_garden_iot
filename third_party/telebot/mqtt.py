import paho.mqtt.client as mqtt
import threading
import json
import logging
import asyncio

logger = logging.getLogger(__name__)


class MQTTClient:
    def __init__(self, config, notification_manager):
        self.config = config
        self.notification_manager = notification_manager
        self.mqtt_client = mqtt.Client()
        self.loop = asyncio.get_event_loop()

        # Initialize the subscribed users set
        self.subscribed_users = set()

        # MQTT Setup
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_mqtt_message
        self.mqtt_client.on_disconnect = self.on_disconnect

        # Reconnect settings
        self.mqtt_client.reconnect_delay_set(min_delay=1, max_delay=120)

    def connect(self):
        """Connect to the MQTT broker."""
        try:
            logger.info("Connecting to MQTT broker...")
            self.mqtt_client.connect(self.config.mqtt_broker, self.config.mqtt_port, keepalive=60)
            self.start_mqtt_loop()
        except Exception as e:
            logger.error(f"Failed to connect to MQTT broker: {e}")

    def on_connect(self, client, userdata, flags, rc):
        """Handle successful connection to the MQTT broker."""
        if rc == 0:
            logger.info(f"Connected to MQTT broker at {self.config.mqtt_broker}:{self.config.mqtt_port}")
            # Subscribe to the topic
            self.mqtt_client.subscribe(self.config.command_channel + "alerts")
            logger.info(f"Subscribed to topic: {self.config.command_channel}alerts")
        else:
            logger.error(f"Failed to connect to MQTT broker, return code {rc}")

    def on_disconnect(self, client, userdata, rc):
        """Handle MQTT disconnection."""
        if rc != 0:
            logger.warning(f"Unexpected MQTT disconnection. Will attempt to reconnect. Reason Code: {rc}")
            try:
                client.reconnect()
            except Exception as e:
                logger.error(f"Failed to reconnect: {e}")

    def on_mqtt_message(self, client, userdata, msg):
        """Handle incoming MQTT messages with a standardized format."""
        try:
            payload_str = msg.payload.decode('utf-8')

            try:
                payload = json.loads(payload_str.replace("'", '"'))
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse MQTT message as JSON: {e}")
                return

            if 'Alerts' in payload:
                alert_message = payload['Alerts']
                logger.info(f"Received message from topic {msg.topic}: {alert_message}")
                logger.info(f"Notifying all subscribed users: {self.subscribed_users}")
                asyncio.run_coroutine_threadsafe(self.notification_manager.notify_users(alert_message), self.loop)
            else:
                logger.error("No 'Alerts' field found in the MQTT message payload.")

        except Exception as e:
            logger.error(f"Error in on_mqtt_message: {e}")

    def mqtt_publish(self, topic, message):
        """Publish a message to an MQTT topic."""
        try:
            logger.info(f"Publishing to {topic}: {message}")
            result = self.mqtt_client.publish(topic, json.dumps(message))
            result.wait_for_publish()  # Make sure the message is sent
            logger.info(f"Published to {topic} with message: {message}")
        except Exception as e:
            logger.error(f"Failed to publish to MQTT: {e}")

    def start_mqtt_loop(self):
        """Start the MQTT loop in a separate thread."""
        def mqtt_loop():
            try:
                logger.info("Starting MQTT loop in a separate thread.")
                self.mqtt_client.loop_forever()
            except Exception as e:
                logger.error(f"Error in MQTT loop: {e}")

        mqtt_thread = threading.Thread(target=mqtt_loop, daemon=True)
        mqtt_thread.start()

    def register_user(self, user_id):
        """Subscribe a user for notifications."""
        if user_id not in self.subscribed_users:
            logger.info(f"Subscribing user {user_id} to notifications...")
            self.subscribed_users.add(user_id)
            self.notification_manager.register_user(user_id)
            logger.info(f"User {user_id} subscribed to notifications.")
        else:
            logger.info(f"User {user_id} is already subscribed.")

