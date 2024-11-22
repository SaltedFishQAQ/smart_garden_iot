import requests
import constants.http as const_h
from http import HTTPMethod
from service.user.logic.base import Common


class Logic(Common):
    def __init__(self, delegate):
        super().__init__(delegate)
        self.influx_base_url = f'{const_h.INFLUX_HOST}:{const_h.SERVICE_PORT_INFLUX}'

    def register_handler(self):
        self.delegate.http_client.add_route(const_h.USER_OPERATION_GET, HTTPMethod.GET, self.list)

    def list(self, params):
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
