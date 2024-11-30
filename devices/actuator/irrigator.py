from devices.biz.base_actuator import BaseActuator


TAG = 'irrigator'


class Irrigator(BaseActuator):
    def __init__(self):
        super().__init__("irrigator")

    def _on(self):
        return "start watering"

    def _off(self):
        return "stop watering"

    def measurement(self) -> str:
        return TAG
