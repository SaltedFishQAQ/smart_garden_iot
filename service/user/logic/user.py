import requests
import constants.http as const_h
from http import HTTPMethod


class Logic:
    def __init__(self, delegate):
        self.delegate = delegate
        self.mysql_base_url = f'{const_h.MYSQL_HOST}:{const_h.SERVICE_PORT_MYSQL}'

    def register_handler(self):
        self.delegate.http_client.add_route(const_h.USER_LOGIN, HTTPMethod.POST, self.login)
        self.delegate.http_client.add_route(const_h.USER_REGISTER, HTTPMethod.POST, self.register)

    def login(self, params):
        resp = requests.post(self.mysql_base_url + const_h.MYSQL_USER_LOGIN, json=params)

        return {
            'code': 0,
            'message': "success",
            'data': resp.json()
        }

    def register(self, params):
        resp = requests.post(self.mysql_base_url + const_h.MYSQL_USER_REGISTER, json=params)

        return {
            'code': 0,
            'message': "success",
            'data': resp.json()
        }
