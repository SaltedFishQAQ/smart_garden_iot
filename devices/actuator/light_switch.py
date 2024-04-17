from devices.biz.base_actuator import BaseActuator


class LightSwitch(BaseActuator):
    def __init__(self):
        super().__init__("light switch")

    def _on(self):
        # TODO: turn on the light
        print("turn on the light")

    def _off(self):
        # TODO: turn off the light
        print("turn off the light")
