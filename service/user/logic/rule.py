import requests
import constants.http as const_h
from http import HTTPMethod


class Logic:
    def __init__(self, delegate):
        self.delegate = delegate
        self.mysql_base_url = f'{const_h.SERVICE_HOST}:{const_h.SERVICE_PORT_MYSQL}'

    def register_handler(self):
        self.delegate.http_client.add_route(const_h.USER_RULE_LIST, HTTPMethod.GET, self.list)
        self.delegate.http_client.add_route(const_h.USER_RULE_SAVE, HTTPMethod.POST, self.save)
        self.delegate.http_client.add_route(const_h.USER_RULE_RUNNING, HTTPMethod.POST, self.running)

    def list(self, params):
        resp = requests.get(self.mysql_base_url + const_h.MYSQL_RULE_LIST, params)

        return {
            'code': 0,
            'message': "success",
            'list': resp.json()['list']
        }

    def save(self, params):
        resp = requests.post(self.mysql_base_url + const_h.MYSQL_RULE_SAVE, json=params)
        if resp.status_code != 200:
            return {
                'code': 500,
                'message': 'sql error'
            }

        return {
            'code': 0,
            'message': "success",
        }

    def running(self, params):
        if 'id' not in params or 'status' not in params:
            return {
                'code': 500,
                'message': 'missing params: id or status'
            }
        resp = requests.post(self.mysql_base_url + const_h.MYSQL_RULE_RUNNING, json=params)
        if resp.status_code != 200:
            return {
                'code': 500,
                'message': 'sql error'
            }

        return {
            'code': 0,
            'message': "success",
        }