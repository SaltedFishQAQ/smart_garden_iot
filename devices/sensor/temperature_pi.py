import json
import Adafruit_DHT

from devices.biz.base_sensor import BaseSensor


class TemperatureSensorPi(BaseSensor):
    def __init__(self):
        super().__init__("temperature pi")
        self._sensor = Adafruit_DHT.DHT11
        self.pin = 4

    def monitor(self) -> str:
        _, temperature = Adafruit_DHT.read_retry(self._sensor, self.pin)
        if temperature is None:
            print('Failed to get reading. Try again!')

        return json.dumps({
            'value': round(temperature, 1)
        })
