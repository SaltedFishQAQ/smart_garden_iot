from devices.biz.base_actuator import BaseActuator


TAG = 'light'


class LightSwitch(BaseActuator):
    def __init__(self):
        super().__init__("light switch")

    def _on(self):
        return "turn on the light"

    def _off(self):
        return "turn off the light"
