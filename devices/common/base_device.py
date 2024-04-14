from .mqtt import MQTTClient


class BaseDevice:
    def __init__(self, device_id, broker, port):
        self.mqtt_client = None
        self.device_id = device_id
        self.broker = broker
        self.port = port

    def init_mqtt_client(self):
        if self.mqtt_client is not None:
            return

        self.mqtt_client = MQTTClient(self.device_id, self.broker, self.port)
        self.mqtt_client.start()

    def remove_mqtt_client(self):
        if self.mqtt_client is None:
            return

        self.mqtt_client.stop()
        self.mqtt_client = None

    def mqtt_listen(self, topic, callback):
        if self.mqtt_client is None:
            return False, "mqtt_client is none"
        self.mqtt_client.subscribe(topic, callback)

        return True, ""

    def mqtt_publish(self, topic, message):
        if self.mqtt_client is None:
            return False, "mqtt_client is none"

        self.mqtt_client.publish(topic, message)
        return True, ""
