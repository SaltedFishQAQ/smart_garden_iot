from common.mqtt import MQTTClient
from common.http_client import HTTPClient


class BaseService:
    def __init__(self, name):
        self.service_name = name
        # mqtt
        self.mqtt_client = None
        self.mqtt_broker = None
        self.mqtt_port = None
        # http
        self.http_client = None
        self.http_host = None
        self.http_port = None

    def init_mqtt_client(self, broker="mqtt.eclipseprojects.io", port=1883):
        if self.mqtt_client is not None:
            return

        self.mqtt_broker = broker
        self.mqtt_port = port
        self.mqtt_client = MQTTClient(self.service_name, broker, port)
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

    def init_http_client(self, host="localhost", port=8080):
        if self.http_client is not None:
            return

        self.http_host = host
        self.http_port = port
        self.http_client = HTTPClient(host, port)
        self.http_client.start()

    def remove_http_client(self):
        if self.http_client is None:
            return

        self.http_client.stop()
        self.http_client = None
