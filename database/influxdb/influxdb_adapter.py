import json
import constants.entity
import constants.mqtt
import constants.http

from common.base_service import BaseService
from database.influxdb.connector import Connector
from http import HTTPMethod
from datetime import datetime


class InfluxdbAdapter(BaseService):
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
        self.mqtt_listen(constants.mqtt.INFLUX_AUTH_BASE_PATH + '+', self.mqtt_data)

    def register_http_handler(self):
        # device data
        self.http_client.add_route(constants.http.TEMPERATURE_GET, HTTPMethod.GET, self.http_temperature_get)
        self.http_client.add_route(constants.http.HUMIDITY_GET, HTTPMethod.GET, self.http_humidity_get)

    def mqtt_data(self, client, userdata, msg):
        measurement = msg.topic.removeprefix(constants.mqtt.INFLUX_AUTH_BASE_PATH)
        if measurement not in self.enable_measurement:
            print(f'mqtt topic invalid: {msg.topic}')
            return
        content = msg.payload.decode('utf-8')
        data_dict = json.loads(content)
        self.db_connector.insert(measurement, data_dict['tags'], data_dict['fields'])

    def http_temperature_get(self, params):
        measurement = constants.entity.TEMPERATURE
        time_cond = []
        filter_cond = None

        if 'device' in params:
            filter_cond = f'r.device_id == "{params["device"]}"'

        if 'start_at' in params:
            start_time = datetime.strptime(params["start_at"], '%Y-%m-%d %H:%M:%S')
            time_cond.append(f'start: {start_time.strftime("%Y-%m-%dT%H:%M:%SZ")}')

        if 'stop_at' in params:
            stop_time = datetime.strptime(params["stop_at"], '%Y-%m-%d %H:%M:%S')
            time_cond.append(f'stop: {stop_time.strftime("%Y-%m-%dT%H:%M:%SZ")}')

        time_range = None
        if len(time_cond) > 0:
            time_range = ", ".join(time_cond)

        result = self.db_connector.query(measurement, time_range=time_range, cond=filter_cond)

        return json.dumps({
            'list': result
        })

    def http_humidity_get(self, params):
        measurement = constants.entity.HUMIDITY

        self.db_connector.query(measurement)



