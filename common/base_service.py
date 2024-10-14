import time
import requests
import threading
import constants.entity
import constants.http as const_h
from common.mqtt import MQTTClient
from common.http_client import HTTPClient


class BaseService:
    def __init__(self, name):
        self.service_name = name
        self.mqtt_broker = None
        self.mqtt_port = None
        self.http_host = None
        self.http_port = None
        # communication
        self.mqtt_client = None
        self.http_client = None
        self.register_url = f'{const_h.MYSQL_HOST}:{const_h.SERVICE_PORT_MYSQL}{const_h.MYSQL_SERVICE_REGISTER}'

    def start(self):
        threading.Thread(target=self._heart_beat).start()

    def init_mqtt_client(self, broker="10.9.0.10", port=1883):
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

    def _heart_beat(self):
        if self.service_name == constants.entity.MYSQL:
            time.sleep(100)

        while True:
            data = {
                'name': self.service_name
            }
            _ = requests.post(self.register_url, json=data)
            time.sleep(60)
