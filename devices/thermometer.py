import json

from devices.biz.base_device import BaseDevice
from devices.sensor.temperature import TemperatureSensor


class Thermometer(BaseDevice):
    def __init__(self, name):
        super().__init__(name, "mqtt.eclipseprojects.io", 1883)
        self.publish_topic = 'iot/lwx123321/test/temperature'
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
