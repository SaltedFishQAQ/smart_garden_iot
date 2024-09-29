import json
import random
from devices.biz.base_sensor import BaseSensor


class GasDetector(BaseSensor):
    def __init__(self):
        super().__init__("gas")

    def monitor(self) -> str:
        return json.dumps({
            'value': round(random.uniform(20, 22), 1)
        })
