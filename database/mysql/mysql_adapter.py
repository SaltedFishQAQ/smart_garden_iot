import json
import constants.entity
import constants.http

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
        result = self.db_connect.query("select * from device")
        print(result)


