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
        self.delegate.http_client.add_route(const_h.USER_DATA_GET, HTTPMethod.GET, self.data_get)
        self.delegate.http_client.add_route(const_h.USER_OPERATION_GET, HTTPMethod.GET, self.data_get)
        self.delegate.http_client.add_route(const_h.USER_MEASUREMENT_LIST, HTTPMethod.GET, self.measurement_list)
        # self.delegate.http_client.add_route(const_h.USER_DATA_MOCK, HTTPMethod.POST, self.mock_data)

    def measurement_list(self, params):
        resp = requests.get(self.influx_base_url + const_h.INFLUX_MEASUREMENT_LIST, params)

        result = []
        if resp.json() is not None:
            result = resp.json()['list']

        return {
            'code': 0,
            'message': "success",
            'list': result
        }

    def data_get(self, params):
        resp = requests.get(self.influx_base_url + const_h.INFLUX_DATA_GET, params)

        result = []
        if resp.json() is not None:
            result = resp.json()['list']

        return {
            'code': 0,
            'message': "success",
            'list': result
        }

    def operation_get(self, params):
        resp = requests.get(self.influx_base_url + const_h.INFLUX_OPERATION_GET, params)

        result = []
        if resp.json() is not None:
            result = resp.json()['list']

        return {
            'code': 0,
            'message': "success",
            'list': result
        }

    # @staticmethod
    # def mock_data(params):
    #     d = MockDevice()
    #     d.init_mock_data(params['number'])
    #
    #     return {
    #         'code': 0,
    #         'message': "success",
    #     }

