import json
import constants.http as const_h
from http import HTTPMethod
from common.time import time_to_str


class Logic:
    def __init__(self, delegate):
        self.delegate = delegate

    def register_handler(self):
        self.delegate.http_client.add_route(const_h.MYSQL_DEVICE_LIST, HTTPMethod.GET, self.list)
        self.delegate.http_client.add_route(const_h.MYSQL_DEVICE_CERTIFIED_LIST, HTTPMethod.GET, self.certified_list)

    def list(self, params):
        records = self.delegate.db_connect.query("select * from device")
        result = []
        for record in records:
            result.append({
                'id': record['id'],
                'name': record['name'],
                'running_status': record['running_status'],
                'auth_status': record['auth_status'],
                'created_at': time_to_str(record['created_at']),
                'updated_at': time_to_str(record['updated_at'])
            })

        return {
            'list': result
        }

    def certified_list(self, params):
        records = self.delegate.db_connect.query("select id, name from device where auth_status = 1")
        result = []
        for record in records:
            result.append({
                'id': record['id'],
                'name': record['name']
            })

        return {
            'list': result
        }
