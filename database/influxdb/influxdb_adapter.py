import os
import json
import constants.entity
import constants.http
import message_broker.channels as mb_channel
import pytz
from common.time import str_to_time, time_convert_timezone
from common.base_service import BaseService
from database.influxdb.connector import Connector
from http import HTTPMethod


class InfluxdbAdapter(BaseService):
    def __init__(self):
        super().__init__(constants.entity.INFLUX)
        self.host = constants.http.SERVICE_HOST
        self.port = constants.http.SERVICE_PORT_INFLUX
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'configuration.json')
        self.conf = json.load(open(config_path))
        self.data_db_connector = Connector(self.conf['url'],
                                           self.conf['token'],
                                           self.conf['org'],
                                           "data")
        self.operation_db_connector = Connector(self.conf['url'],
                                                self.conf['token'],
                                                self.conf['org'],
                                                "data")
        self.data_channel = mb_channel.STORAGE_DATA  # channel for store data
        self.operation_channel = mb_channel.STORAGE_OPERATION  # channel for store operation
        self.enable_measurement = {
            constants.entity.TEMPERATURE: True,
            constants.entity.HUMIDITY: True,
            constants.entity.LIGHT: True,
            constants.entity.GATE: True,
            constants.entity.IRRIGATOR: True,
            constants.entity.OXYGEN: True,
        }

    def start(self):
        super().start()
        self.init_mqtt_client()
        self.init_http_client(host=self.host, port=self.port)

    def stop(self):
        self.remove_mqtt_client()
        self.remove_http_client()

    def register_mqtt_service(self):
        # device data
        self.mqtt_listen(self.data_channel + '+', self.mqtt_data)
        # device operation
        self.mqtt_listen(self.operation_channel, self.mqtt_operation)

    def register_http_handler(self):
        self.http_client.add_route(constants.http.INFLUX_MEASUREMENT_LIST, HTTPMethod.GET, self.http_measurement_list)
        # device data
        self.http_client.add_route(constants.http.INFLUX_DATA_GET, HTTPMethod.GET, self.http_data_get)
        # data count
        self.http_client.add_route(constants.http.INFLUX_DATA_COUNT, HTTPMethod.GET, self.http_data_count)
        # device operation
        self.http_client.add_route(constants.http.INFLUX_OPERATION_GET, HTTPMethod.GET, self.http_operation_get)

    def mqtt_data(self, client, userdata, msg):
        measurement = msg.topic.removeprefix(self.data_channel)
        if measurement not in self.enable_measurement:
            print(f'mqtt topic invalid: {msg.topic}')
            return
        content = msg.payload.decode('utf-8')
        data_dict = json.loads(content)
        self.data_db_connector.insert(measurement, data_dict['tags'], data_dict['fields'])

    def mqtt_operation(self, client, userdata, msg):
        content = msg.payload.decode('utf-8')
        data_dict = json.loads(content)
        self.operation_db_connector.insert("default", data_dict['tags'], data_dict['fields'])

    def http_measurement_list(self, param):
        result = self.data_db_connector.measurement_list()

        return {
            'list': result
        }

    def http_data_count(self, params):
        measurement = ''
        if 'measurement' in params:
            measurement = params['measurement']

        counts = self.data_db_connector.count(measurement)

        return {
            'count': counts
        }

    def http_data_get(self, params):
        if 'measurement' not in params:
            return {
                'list': []
            }

        measurement = params['measurement']
        time_cond = []
        filter_cond = None

        if 'name' in params:
            filter_cond = f'r.device == "{params["name"]}"'

        if 'start_at' in params:
            start_time = str_to_time(params["start_at"])
            time_cond.append(f'start: {start_time.strftime("%Y-%m-%dT%H:%M:%SZ")}')

        if 'stop_at' in params:
            stop_time = str_to_time(params["stop_at"])
            time_cond.append(f'stop: {stop_time.strftime("%Y-%m-%dT%H:%M:%SZ")}')

        if 'page' not in params:
            params['page'] = 1
        else:
            params['page'] = int(params['page'])

        if 'size' not in params:
            params['size'] = 10
        else:
            params['size'] = int(params['size'])

        time_range = None
        if len(time_cond) > 0:
            time_range = ", ".join(time_cond)

        result = self.data_db_connector.query(measurement, time_range=time_range, cond=filter_cond,
                                              page=params['page'], size=params['size'])

        for i in range(len(result)):
            result[i]['created_at'] = time_convert_timezone(result[i]['created_at'], pytz.utc, 'Europe/Rome')

        return {
            'list': result
        }

    def http_operation_get(self, params):
        time_cond = []
        filter_cond = None

        if 'name' in params:
            filter_cond = f'r.device == "{params["name"]}"'

        if 'start_at' in params:
            start_time = str_to_time(params["start_at"])
            time_cond.append(f'start: {start_time.strftime("%Y-%m-%dT%H:%M:%SZ")}')

        if 'stop_at' in params:
            stop_time = str_to_time(params["stop_at"])
            time_cond.append(f'stop: {stop_time.strftime("%Y-%m-%dT%H:%M:%SZ")}')

        if 'page' not in params:
            params['page'] = 1
        else:
            params['page'] = int(params['page'])

        if 'size' not in params:
            params['size'] = 10
        else:
            params['size'] = int(params['size'])

        time_range = None
        if len(time_cond) > 0:
            time_range = ", ".join(time_cond)

        result = self.operation_db_connector.query("default", time_range=time_range, cond=filter_cond,
                                                   page=params['page'], size=params['size'])

        return {
            'list': result
        }
