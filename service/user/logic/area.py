import requests
import constants.http as const_h
from http import HTTPMethod
from service.user.logic.base import Common


class Logic(Common):
    def __init__(self, delegate):
        super().__init__(delegate)

    def register_handler(self):
        self.delegate.http_client.add_route(const_h.USER_AREA_LIST, HTTPMethod.GET, self.list)
        self.delegate.http_client.add_route(const_h.USER_AREA_CREATE, HTTPMethod.POST, self.create)
        self.delegate.http_client.add_route(const_h.USER_AREA_UPDATE, HTTPMethod.PUT, self.update)

    def list(self, params):
        if err := self.check_params(params, ['user_id']):
            return err

        return {
            'code': 0,
            'message': "success",
            'list': self.get_area_list(params)
        }

    def create(self, params):
        if err := self.check_params(params, ['user_id']):
            return err

        user = self.get_user(params['user_id'])
        if user is None or user['role'] != 1:
            return {
                'code': 500,
                'message': 'no operation permission'
            }

        resp = requests.post(self.mysql_base_url + const_h.MYSQL_AREA_SAVE, json=params)

        return {
            'code': 0,
            'message': "success",
            'data': {
                'id': resp.json()['row']
            }
        }

    def update(self, params):
        if err := self.check_params(params, ['id', 'user_id']):
            return err

        user = self.get_user(params['user_id'])
        if user is None or user['role'] != 1:
            return {
                'code': 500,
                'message': 'no operation permission'
            }

        _ = requests.post(self.mysql_base_url + const_h.MYSQL_AREA_SAVE, json=params)

        return {
            'code': 0,
            'message': "success",
        }
