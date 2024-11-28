import json
import random
from devices.biz.base_sensor import BaseSensor


TAG = 'gas'


class GasDetector(BaseSensor):
    def __init__(self):
        super().__init__("gas")

    def monitor(self) -> str:
        return json.dumps({
            'value': float(round(random.uniform(20, 22), 1))
        })

    def measurement(self) -> str:
        return 'gas'
