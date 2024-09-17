import os
import json
import random
import time
import constants.entity as entity
import message_broker.channels as mb_channel
from devices.biz.base_device import BaseDevice


class MockDevice(BaseDevice):
    def __init__(self):
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'configuration.json')
        self.conf = json.load(open(config_path))
        super().__init__("mock_device", self.conf['broker'], self.conf['port'])
        self.publish_topic = mb_channel.STORAGE_DATA
        self.init_mqtt_client()

    def init_mock_data(self, number):
        sensors = [entity.TEMPERATURE, entity.HUMIDITY]
        actuators = [entity.LIGHT, entity.GATE, entity.IRRIGATOR]

        # sensor
        for measurement in sensors:
            for _ in range(number):
                self.send(measurement, {
                    'value': round(random.uniform(10.0, 30.0), 1)
                })
                time.sleep(1)
        # actuator
        for measurement in actuators:
            for _ in range(number):
                self.send(measurement, {
                    'opt': random.choice(["on", "off"])
                })
                time.sleep(1)

    def send(self, measurement, fields):
        mqtt_data = {
            'tags': {
                'device': self.device_name,
            },
            'fields': fields,
        }
        self.mqtt_publish(self.publish_topic + measurement, json.dumps(mqtt_data))
