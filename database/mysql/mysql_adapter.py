import os
import json
import constants.entity
import constants.http

from common.base_service import BaseService
from database.mysql.connector import Connector
from database.mysql.logic import device, user, service, rule


class MysqlAdapter(BaseService):
    def __init__(self):
        super().__init__(constants.entity.MYSQL)
        self.host = constants.http.SERVICE_HOST
        self.port = constants.http.SERVICE_PORT_MYSQL
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'configuration.json')
        self.conf = json.load(open(config_path))
        self.db_connect = Connector(self.conf['host'],
                                    self.conf['port'],
                                    self.conf['user'],
                                    self.conf['password'],
                                    self.conf['database'])

    def start(self):
        super().start()
        self.init_http_client(host=self.host, port=self.port)

    def stop(self):
        self.remove_http_client()

    def register_http_service(self):
        device.Logic(self).register_handler()
        user.Logic(self).register_handler()
        service.Logic(self).register_handler()
        rule.Logic(self).register_handler()
