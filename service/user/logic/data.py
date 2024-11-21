import requests
import constants.http as const_h
from http import HTTPMethod
from service.user.logic.base import Common


class Logic(Common):
    def __init__(self, delegate):
        super().__init__(delegate)
        self.influx_base_url = f'{const_h.INFLUX_HOST}:{const_h.SERVICE_PORT_INFLUX}'

    def register_handler(self):
        self.delegate.http_client.add_route(const_h.USER_DATA_GET, HTTPMethod.GET, self.data_get)
        self.delegate.http_client.add_route(const_h.USER_DATA_COUNT, HTTPMethod.GET, self.data_count)
        self.delegate.http_client.add_route(const_h.USER_MEASUREMENT_LIST, HTTPMethod.GET, self.measurement_list)

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

    def data_count(self, params):
        self.match_area_names(params)
        resp = requests.get(self.influx_base_url + const_h.INFLUX_DATA_COUNT, params)

        return {
            'code': 0,
            'message': "success",
            'count': resp.json()['count']
        }

    def data_get(self, params):
        self.match_area_names(params)
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
        self.match_area_names(params)
        resp = requests.get(self.influx_base_url + const_h.INFLUX_OPERATION_GET, params)

        result = []
        if resp.json() is not None:
            result = resp.json()['list']

        return {
            'code': 0,
            'message': "success",
            'list': result
        }
