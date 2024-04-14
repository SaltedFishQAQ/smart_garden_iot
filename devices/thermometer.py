import json

from common.base_device import BaseDevice
from sensor.temperature import TemperatureSensor


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

    def record_data(self, data):
        data_dict = json.loads(data)
        key = 'temperature'
        if key not in data_dict:
            print(f"data missing temperature value, data: {data}")
            return

        temp = data_dict[key]
        self.mqtt_publish(self.publish_topic, temp)
