import requests
import constants.http as const_h
from http import HTTPMethod
from service.user.logic.base import Common


class Logic(Common):
    def __init__(self, delegate):
        super().__init__(delegate)

    def register_handler(self):
        self.delegate.http_client.add_route(const_h.USER_SCHEDULE_LIST, HTTPMethod.GET, self.list)
        self.delegate.http_client.add_route(const_h.USER_SCHEDULE_COUNT, HTTPMethod.GET, self.count)
        self.delegate.http_client.add_route(const_h.USER_SCHEDULE_CREATE, HTTPMethod.POST, self.create)
        self.delegate.http_client.add_route(const_h.USER_SCHEDULE_UPDATE, HTTPMethod.PUT, self.update)
        self.delegate.http_client.add_route(const_h.USER_SCHEDULE_RUNNING, HTTPMethod.POST, self.running)

    def list(self, params):
        self.match_device_names(params)
        resp = requests.get(self.mysql_base_url + const_h.MYSQL_SCHEDULE_LIST, params)

        return {
            'code': 0,
            'message': "success",
            'list': resp.json()['list']
        }

    def count(self, params):
        self.match_device_names(params)
        resp = requests.get(self.mysql_base_url + const_h.MYSQL_SCHEDULE_COUNT, params)

        return {
            'code': 0,
            'message': "success",
            'count': resp.json()['count']
        }

    def create(self, params):
        resp = requests.post(self.mysql_base_url + const_h.MYSQL_SCHEDULE_SAVE, json=params)
        if resp.status_code != 200:
            return {
                'code': 500,
                'message': 'sql error'
            }

        if resp.json() is None:
            return {
                'code': 500,
                'message': "sql error",
            }

        return {
            'code': 0,
            'message': "success",
            'data': {
                'id': resp.json()['row']
            }
        }

    def update(self, params):
        if 'id' not in params:
            return {
                'code': 500,
                'message': 'missing params: id'
            }
        resp = requests.post(self.mysql_base_url + const_h.MYSQL_SCHEDULE_SAVE, json=params)
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
        resp = requests.post(self.mysql_base_url + const_h.MYSQL_SCHEDULE_RUNNING, json=params)
        if resp.status_code != 200:
            return {
                'code': 500,
                'message': 'sql error'
            }

        return {
            'code': 0,
            'message': "success",
        }
