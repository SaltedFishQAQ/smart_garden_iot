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
        self.storage_channel = mb_channel.STORAGE_DATA  # channel for store data
        self.certified_list = []  # verified device
        self.mysql_base_url = f'{constants.http.MYSQL_HOST}:{constants.http.SERVICE_PORT_MYSQL}'
        self.running = False

    def start(self):
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

    def mqtt_data(self, client, userdata, msg):
        content = msg.payload.decode('utf-8')
        data_dict = json.loads(content)
        print(data_dict)
        if 'tags' not in data_dict or 'device' not in data_dict['tags']:
            print(f"topic {msg.topic} message without device")
            return

        is_certified = False
        device = data_dict['tags']['device']
        for item in self.certified_list:
            if device == item['name']:
                is_certified = True
                break

        if is_certified is not True:
            print(f"device: {device}, is not certified")
            return

        entity = msg.topic.removeprefix(self.data_channel)
        self.mqtt_publish(self.storage_channel + entity, msg.payload)
