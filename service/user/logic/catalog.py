import requests
import constants.http as const_h
from http import HTTPMethod


class Logic:
    def __init__(self, delegate):
        self.delegate = delegate
        self.mysql_base_url = f'{const_h.MYSQL_HOST}:{const_h.SERVICE_PORT_MYSQL}'

    def register_handler(self):
        self.delegate.http_client.add_route(const_h.USER_CATALOG_SERVICE, HTTPMethod.GET, self.service_list)
        self.delegate.http_client.add_route(const_h.USER_CATALOG_DEVICE, HTTPMethod.GET, self.device_list)
        self.delegate.http_client.add_route(const_h.USER_CATALOG_DEVICE_COUNT, HTTPMethod.GET, self.device_count)

    def service_list(self, params):
        resp = requests.get(self.mysql_base_url + const_h.MYSQL_SERVICE_LIST, params)

        return {
            'code': 0,
            'message': "success",
            'list': resp.json()['list']
        }

    def device_list(self, params):
        resp = requests.get(self.mysql_base_url + const_h.MYSQL_DEVICE_LIST, params)

        return {
            'code': 0,
            'message': "success",
            'list': resp.json()['list']
        }

    def device_count(self, params):
        resp = requests.get(self.mysql_base_url + const_h.MYSQL_DEVICE_COUNT, params)

        return {
            'code': 0,
            'message': "success",
            'count': resp.json()['count']
        }
