import requests
import constants.http as const_h
import constants.entity as const_e
from devices.mock_device import MockDevice
from http import HTTPMethod


class Logic:
    def __init__(self, delegate):
        self.delegate = delegate
        self.mysql_base_url = f'{const_h.MYSQL_HOST}:{const_h.SERVICE_PORT_MYSQL}'
        self.influx_base_url = f'{const_h.INFLUX_HOST}:{const_h.SERVICE_PORT_INFLUX}'

    def register_handler(self):
        self.delegate.http_client.add_route(const_h.USER_DATA_ENTITY_LIST, HTTPMethod.GET, self.entity_list)
        self.delegate.http_client.add_route(const_h.USER_DATA_TEMPERATURE, HTTPMethod.GET, self.temperature_data)
        self.delegate.http_client.add_route(const_h.USER_DATA_HUMIDITY, HTTPMethod.GET, self.humidity_data)
        self.delegate.http_client.add_route(const_h.USER_DATA_LIGHT, HTTPMethod.GET, self.light_data)
        self.delegate.http_client.add_route(const_h.USER_DATA_MOCK, HTTPMethod.POST, self.mock_data)

    @staticmethod
    def entity_list(params):
        result = [
            {'entity': const_e.TEMPERATURE, 'desc': 'data of temperature'},
            {'entity': const_e.HUMIDITY, 'desc': 'data of humidity'},
            {'entity': const_e.LIGHT, 'desc': 'data of light status'}
        ]

        return result

    def temperature_data(self, params):
        resp = requests.get(self.influx_base_url + const_h.INFLUX_TEMPERATURE_GET, params)

        result = []
        if resp.json() is not None:
            result = resp.json()['list']

        return {
            'code': 0,
            'message': "success",
            'list': result
        }

    def humidity_data(self, params):
        resp = requests.get(self.influx_base_url + const_h.INFLUX_HUMIDITY_GET, params)

        result = []
        if resp.json() is not None:
            result = resp.json()['list']

        return {
            'code': 0,
            'message': "success",
            'list': result
        }

    def light_data(self, params):
        resp = requests.get(self.influx_base_url + const_h.INFLUX_LIGHT_GET, params)

        result = []
        if resp.json() is not None:
            result = resp.json()['list']

        return {
            'code': 0,
            'message': "success",
            'list': result
        }

    @staticmethod
    def mock_data(params):
        d = MockDevice()
        d.init_mock_data(params['number'])

        return {
            'code': 0,
            'message': "success",
        }

