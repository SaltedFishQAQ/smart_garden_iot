import json
import constants.mqtt

from devices.biz.base_device import BaseDevice
from devices.sensor.temperature import TemperatureSensor


class Thermometer(BaseDevice):
    def __init__(self, name):
        self.conf = json.load(open('./configuration.json'))
        super().__init__(name, self.conf['broker'], self.conf['port'])
        self.publish_topic = constants.mqtt.TEMPERATURE_TOPIC
        self.sensor = TemperatureSensor()
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
            print(f"data missing temperature value, data: {data}")
            return

        mqtt_data = {
            'tags': {
                'device_id': self.device_id,
            },
            'fields': data,
        }
        self.mqtt_publish(self.publish_topic, json.dumps(mqtt_data))
