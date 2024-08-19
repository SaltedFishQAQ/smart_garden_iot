import os
import json
import random
import time
import message_broker.channels as mb_channel
from devices.biz.base_device import BaseDevice


class MockDevice(BaseDevice):
    def __init__(self):
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'configuration.json')
        self.conf = json.load(open(config_path))
        super().__init__("mock_device", self.conf['broker'], self.conf['port'])
        self.publish_topic = mb_channel.STORAGE_DATA + "temperature"
        self.init_mqtt_client()

    def init_mock_data(self, number):
        for _ in range(number):
            mqtt_data = {
                'tags': {
                    'device': self.device_name,
                },
                'fields': {
                    'value': round(random.uniform(10.0, 30.0), 1)
                },
            }
            self.mqtt_publish(self.publish_topic, json.dumps(mqtt_data))
            time.sleep(1)
