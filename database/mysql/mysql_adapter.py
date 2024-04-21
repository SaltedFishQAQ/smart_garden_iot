import json
import constants.entity
import constants.http
from common.time import time_to_str

from common.base_service import BaseService
from database.mysql.connector import Connector
from http import HTTPMethod


class MysqlAdapter(BaseService):
    def __init__(self):
        super().__init__(constants.entity.MYSQL)
        self.conf = json.load(open('./configuration.json'))
        self.db_connect = Connector(self.conf['host'],
                                    self.conf['port'],
                                    self.conf['user'],
                                    self.conf['password'],
                                    self.conf['database'])

    def start(self):
        self.init_http_client()

    def stop(self):
        self.remove_http_client()

    def register_http_service(self):
        self.http_client.add_route(constants.http.MYSQL_DEVICE_LIST, HTTPMethod.GET, self.http_device_list)

    def http_device_list(self, params):
        records = self.db_connect.query("select * from device")
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

        return json.dumps({
            'list': result
        })
