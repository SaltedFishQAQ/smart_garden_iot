import json
import constants.entity
import constants.http

from common.base_service import BaseService
from database.mysql.connector import Connector
from database.mysql.logic import device, user


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
        device.Logic(self).register_handler()
        user.Logic(self).register_handler()
