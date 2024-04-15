from common.mqtt import MQTTClient


class BaseAdapter:
    def __init__(self, adapter_id):
        self.mqtt_client = None
        self.adapter_id = adapter_id
        self.broker = "mqtt.eclipseprojects.io"
        self.port = 1883
        # TODO:
        self.routes = {}

    def init_mqtt_client(self, broker, port):
        if self.mqtt_client is not None:
            return

        self.broker = broker
        self.port = port
        self.mqtt_client = MQTTClient(self.adapter_id, broker, port)
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

    def init_http_client(self):
        # TODO: add http client implement
        print(self.adapter_id)

    def add_http_route(self, route, handler):
        self.routes[route] = handler
