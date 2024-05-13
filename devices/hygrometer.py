import json
import constants.entity
import message_broker.channels as mb_channel

from devices.biz.base_device import BaseDevice
from devices.sensor.humidity import HumiditySensor


class Hygrometer(BaseDevice):
    def __init__(self, name):
        self.conf = json.load(open('./configuration.json'))
        super().__init__(name, self.conf['broker'], self.conf['port'])
        self.publish_topic = mb_channel.DEVICE_DATA + constants.entity.HUMIDITY
        self.sensor = HumiditySensor()
        self.sensor.receiver = self.record_data
        self.init_mqtt_client()
        self.running = False

    def start(self):
        self.sensor.start()
        self.running = True

    def stop(self):
        self.sensor.stop()
        self.running = False

    def record_data(self, data_str):
        data = json.loads(data_str)
        if 'value' not in data:
            print("data missing humidity value, data: {}".format(data))
            return

        mqtt_data = {
            'tags': {
                'device': self.device_name,
            },
            'fields': data,
        }
        self.mqtt_publish(self.publish_topic, json.dumps(mqtt_data))
