import json
import constants.entity
import constants.mqtt
import constants.http
import requests

from common.base_service import BaseService


class AuthService(BaseService):
    def __init__(self):
        super().__init__(constants.entity.AUTH_SERVICE)
        self.certified_list = []

    def start(self):
        self.get_certified_device()
        self.init_mqtt_client()

    def stop(self):
        self.remove_mqtt_client()
        self.remove_http_client()

    def get_certified_device(self):
        resp = requests.get('http://127.0.0.1:8080' + constants.http.MYSQL_DEVICE_CERTIFIED_LIST)
        resp_data = resp.json()
        self.certified_list = resp_data['list']

    def register_mqtt_service(self):
        # device data
        self.mqtt_listen(constants.mqtt.INFLUX_BASE_PATH + '+', self.mqtt_data)

    def mqtt_data(self, client, userdata, msg):
        content = msg.payload.decode('utf-8')
        data_dict = json.loads(content)
        print(data_dict)
        if 'tags' not in data_dict or 'device_id' not in data_dict['tags']:
            print(f"topic {msg.topic} without device_id")
            return

        is_certified = False
        device_id = data_dict['tags']['device_id']
        for item in self.certified_list:
            if device_id == item['name']:
                is_certified = True

        if is_certified is not True:
            return

        entity = msg.topic.removeprefix(constants.mqtt.INFLUX_BASE_PATH)
        auth_topic = constants.mqtt.INFLUX_AUTH_BASE_PATH + entity
        self.mqtt_publish(auth_topic, msg.payload)
