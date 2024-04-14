import json

from devices.common.base_sensor import BaseSensor


class TemperatureSensor(BaseSensor):
    def __init__(self):
        super().__init__("temperature")

    def monitor(self) -> str:
        # TODO: Raspberry Pi get temperature interface
        return json.dumps({
            'temperature': 17
        })
