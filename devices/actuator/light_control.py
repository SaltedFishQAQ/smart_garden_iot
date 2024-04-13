from devices.common.base_actuator import BaseActuator


class LightControl(BaseActuator):
    def __init__(self):
        super().__init__("light_control")

    def _on(self):
        # TODO: turn on the light
        print("turn on the light")

    def _off(self):
        # TODO: turn off the light
        print("turn off the light")
