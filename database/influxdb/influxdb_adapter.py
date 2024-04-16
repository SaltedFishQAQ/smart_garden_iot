import json

from database.common.base_adapter import BaseAdapter


class InfluxdbAdapter(BaseAdapter):
    def __init__(self):
        super().__init__("influxdb")

    def start(self):
        self.init_mqtt_client()
        self.init_http_client()

    def stop(self):
        self.remove_mqtt_client()
        self.remove_http_client()

    def register_mqtt_service(self):
        # device data
        self.mqtt_listen('iot/lwx123321/test/+',  self.mqtt_data)

    def mqtt_data(self, client, userdata, msg):
        content = msg.payload.decode('utf-8')
        data_dict = json.loads(content)
        print(f'topic: {msg.topic}')
        print(f'data: {data_dict}')
        # TODO: insert sql
