import json
import random

from devices.biz.base_sensor import BaseSensor


class TemperatureSensor(BaseSensor):
    def __init__(self):
        super().__init__("temperature")

    def monitor(self) -> str:
        # TODO: Raspberry Pi get temperature interface
        return json.dumps({
            'value': round(random.uniform(10.0, 30.0), 1)
        })
