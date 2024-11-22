import requests
import constants.http as const_h
from http import HTTPMethod
from service.user.logic.base import Common


class Logic(Common):
    def __init__(self, delegate):
        super().__init__(delegate)

    def register_handler(self):
        self.delegate.http_client.add_route(const_h.USER_LOGIN, HTTPMethod.POST, self.login)
        self.delegate.http_client.add_route(const_h.USER_REGISTER, HTTPMethod.POST, self.register)
        self.delegate.http_client.add_route(const_h.USER_LIST, HTTPMethod.GET, self.list)

    def list(self, params):
        user = self.get_user()
        if user is None:
            return {
                'code': 0,
                'message': "success",
                'list': []
            }
        if user['role'] != 1:
            params['id'] = user['id']
        resp = requests.get(self.mysql_base_url + const_h.MYSQL_USER_LIST, params)

        return {
            'code': 0,
            'message': "success",
            'list': resp.json()['list']
        }

    def login(self, params):
        resp = requests.post(self.mysql_base_url + const_h.MYSQL_USER_LOGIN, json=params)
        self.delegate.http_client.set_user(resp.json())

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
