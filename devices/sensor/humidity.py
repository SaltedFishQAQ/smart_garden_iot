import json
import Adafruit_DHT

from devices.biz.base_sensor import BaseSensor


class HumiditySensor(BaseSensor):
    def __init__(self):
        super().__init__("humidity")
        self._sensor = Adafruit_DHT.DHT11
        self.pin = 4

    def monitor(self) -> str:
        humidity, _ = Adafruit_DHT.read_retry(self._sensor, self.pin)
        if humidity is None:
            print('Failed to get reading. Try again!')

        return json.dumps({
            'value': round(humidity, 1)
        })
