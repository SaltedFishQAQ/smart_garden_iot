import json
import time
import constants.entity
import constants.http
import message_broker.channels as mb_channel
import requests
import threading

from common.base_service import BaseService


class AuthService(BaseService):
    def __init__(self):
        super().__init__(constants.entity.AUTH_SERVICE)
        self.data_channel = mb_channel.DEVICE_DATA  # channel for get data
        self.data_storage_channel = mb_channel.STORAGE_DATA  # channel for store data
        self.operation_channel = mb_channel.DEVICE_OPERATION  # channel for get operation
        self.operation_storage_channel = mb_channel.STORAGE_OPERATION  # channel for store operation
        self.certified_list = []  # verified device
        self.mysql_base_url = f'{constants.http.MYSQL_HOST}:{constants.http.SERVICE_PORT_MYSQL}'
        self.running = False

    def start(self):
        super().start()
        self.running = True
        threading.Thread(target=self._get_certified_device).start()
        self.init_mqtt_client()

    def stop(self):
        self.running = False
        self.remove_mqtt_client()
        self.remove_http_client()

    def _get_certified_device(self):
        # reload certified list each 60 seconds
        while self.running:
            resp = requests.get(self.mysql_base_url + constants.http.MYSQL_DEVICE_CERTIFIED_LIST)
            resp_data = resp.json()
            self.certified_list = resp_data['list']
            time.sleep(60)

    def register_mqtt_service(self):
        # device data
        self.mqtt_listen(self.data_channel + '+', self.mqtt_data)
        # device operation
        self.mqtt_listen(self.operation_channel, self.mqtt_operation)

    def is_certified(self, name):
        for item in self.certified_list:
            if name == item['name']:
                return True
        return False

    def mqtt_data(self, client, userdata, msg):
        if self.do_verify(msg) is False:
            return

        entity = msg.topic.removeprefix(self.data_channel)
        self.mqtt_publish(self.data_storage_channel + entity, msg.payload)

    def mqtt_operation(self, client, userdata, msg):
        if self.do_verify(msg) is False:
            return

        self.mqtt_publish(self.operation_storage_channel, msg.payload)

    def do_verify(self, msg):
        content = msg.payload.decode('utf-8')
        data_dict = json.loads(content)
        if 'tags' not in data_dict or 'device' not in data_dict['tags']:
            self.logger.warning(f'topic {msg.topic} message without device, content: {content}')
            return False

        name = data_dict['tags']['device']
        if self.is_certified(name) is False:
            self.logger.warning(f'device: {name}, is not certified')
            return False
        return True
