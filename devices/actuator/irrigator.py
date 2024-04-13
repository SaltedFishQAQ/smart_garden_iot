from devices.common.base_actuator import BaseActuator


class Irrigator(BaseActuator):
    def __init__(self):
        super().__init__("irrigator")

    def _on(self):
        # TODO: start spraying
        print("start spraying")

    def _off(self):
        # TODO: stop spraying
        print("stop spraying")
