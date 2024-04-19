import json
import constants.entity
import constants.mqtt
import constants.http

from database.biz.base_adapter import BaseAdapter
from database.influxdb.connector import Connector
from http import HTTPMethod


class InfluxdbAdapter(BaseAdapter):
    def __init__(self):
        super().__init__(constants.entity.INFLUX)
        self.conf = json.load(open('./configuration.json'))
        self.db_connector = Connector(self.conf['url'],
                                      self.conf['token'],
                                      self.conf['org'],
                                      self.conf['bucket'])
        self.enable_measurement = {
            constants.entity.TEMPERATURE: True,
            constants.entity.HUMIDITY: True
        }

    def start(self):
        self.init_mqtt_client()
        self.init_http_client()

    def stop(self):
        self.remove_mqtt_client()
        self.remove_http_client()

    def register_mqtt_service(self):
        # device data
        self.mqtt_listen(constants.mqtt.INFLUX_BASE_PATH + '+', self.mqtt_data)

    def register_http_handler(self):
        # device data
        self.http_client.add_route(constants.http.TEMPERATURE_GET, HTTPMethod.GET, self.http_temperature_get)
        self.http_client.add_route(constants.http.HUMIDITY_GET, HTTPMethod.GET, self.http_humidity_get)

    def mqtt_data(self, client, userdata, msg):
        measurement = msg.topic.removeprefix(constants.mqtt.INFLUX_BASE_PATH)
        if measurement not in self.enable_measurement:
            print(f'mqtt topic invalid: {msg.topic}')
            return
        content = msg.payload.decode('utf-8')
        data_dict = json.loads(content)
        self.db_connector.insert(measurement, data_dict['tags'], data_dict['fields'])

    def http_temperature_get(self, params):
        measurement = constants.entity.TEMPERATURE

        self.db_connector.query(measurement)

    def http_humidity_get(self, params):
        measurement = constants.entity.HUMIDITY

        self.db_connector.query(measurement)



