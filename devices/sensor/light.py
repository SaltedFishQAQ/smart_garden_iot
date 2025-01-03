import json
import random
from datetime import datetime, time
from devices.biz.base_sensor import BaseSensor


TAG = "light"


class LightSensor(BaseSensor):
    def __init__(self):
        super().__init__("light")

    def monitor(self) -> str:
        now = datetime.now().time()
        sunset = time(18, 0)
        sunrise = time(6, 0)

        if sunrise <= now < sunset:
            value = 25
            random_adjustment = random.uniform(-5, 5)
            value = int(round(value + random_adjustment))
        else:
            value = 0

        return json.dumps({
            'value': value
        })

    def measurement(self) -> str:
        return TAG
