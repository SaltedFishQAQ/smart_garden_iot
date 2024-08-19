import constants.entity
import constants.http
from common.base_service import BaseService
from service.user.logic import data, device, catalog, rule, user


class UserService(BaseService):
    def __init__(self):
        super().__init__(constants.entity.USER_SERVICE)
        self.host = constants.http.SERVICE_HOST
        self.port = constants.http.SERVICE_PORT_USER

    def start(self):
        self.init_mqtt_client()
        self.init_http_client(host=self.host, port=self.port)

    def stop(self):
        self.remove_http_client()
        self.remove_mqtt_client()

    def register_http_service(self):
        data.Logic(self).register_handler()
        device.Logic(self).register_handler()
        catalog.Logic(self).register_handler()
        rule.Logic(self).register_handler()
        user.Logic(self).register_handler()
