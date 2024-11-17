import constants.entity
import constants.http
import json
import message_broker.channels as mb_channel
from common.base_service import BaseService
from service.user.logic import data, device, catalog, rule, user, schedule, operation, area


class UserService(BaseService):
    def __init__(self):
        super().__init__(constants.entity.USER_SERVICE)
        self.host = constants.http.SERVICE_HOST
        self.port = constants.http.SERVICE_PORT_USER
        self.status_topic = mb_channel.DEVICE_STATUS
        self.device_status = {}

    def start(self):
        super().start()
        self.init_mqtt_client()
        self.init_http_client(host=self.host, port=self.port)
        self.mqtt_listen(self.status_topic + "+", self.record_device_status)

    def stop(self):
        self.remove_http_client()
        self.remove_mqtt_client()

    def register_http_service(self):
        area.Logic(self).register_handler()
        data.Logic(self).register_handler()
        device.Logic(self).register_handler()
        catalog.Logic(self).register_handler()
        rule.Logic(self).register_handler()
        user.Logic(self).register_handler()
        schedule.Logic(self).register_handler()
        operation.Logic(self).register_handler()

    def record_device_status(self, client, userdata, msg):
        content = msg.payload.decode('utf-8')
        data_dict = json.loads(content)
        name = msg.topic.removeprefix(self.status_topic)
        self.device_status[name] = data_dict
