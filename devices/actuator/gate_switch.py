from devices.biz.base_actuator import BaseActuator


TAG = 'gate'


class GateSwitch(BaseActuator):
    def __init__(self):
        super().__init__("gate switch")

    def _on(self):
        return "open the gate"

    def _off(self):
        return "close the gate"

    def measurement(self) -> str:
        return TAG
