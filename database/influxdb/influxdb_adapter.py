import json

from database.biz.base_adapter import BaseAdapter
from database.influxdb.connector import Connector
from http import HTTPMethod


class InfluxdbAdapter(BaseAdapter):
    def __init__(self):
        super().__init__("influxdb")
        self.conf = json.load(open('./configuration.json'))
        self.db_connector = Connector(self.conf['url'],
                                      self.conf['token'],
                                      self.conf['org'],
                                      self.conf['bucket'])

    def start(self):
        self.init_mqtt_client()
        self.init_http_client()

    def stop(self):
        self.remove_mqtt_client()
        self.remove_http_client()

    def register_mqtt_service(self):
        # device data
        self.mqtt_listen('iot/lwx123321/test/+',  self.mqtt_data)

    def register_http_handler(self):
        # device data
        self.http_client.add_route('/device/temperature', HTTPMethod.GET, self.http_temperature_get)
        self.http_client.add_route('/device/humidity', HTTPMethod.GET, self.http_humidity_get)

    def mqtt_data(self, client, userdata, msg):
        paths = msg.topic.split('/')
        if len(paths) < 4 or paths[3] == '':
            print(f'mqtt topic invalid: {msg.topic}')
            return
        measurement = paths[3]
        content = msg.payload.decode('utf-8')
        data_dict = json.loads(content)
        self.db_connector.insert(measurement, data_dict['tags'], data_dict['fields'])

    def http_temperature_get(self, params):
        measurement = "temperature"

        self.db_connector.query(measurement)

    def http_humidity_get(self, params):
        measurement = "humidity"

        self.db_connector.query(measurement)



