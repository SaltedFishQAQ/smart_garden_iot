from devices.biz.base_actuator import BaseActuator


class OxygenValve(BaseActuator):
    def __init__(self):
        super().__init__("oxygen valve")

    def _on(self):
        return "open the oxygen valve"

    def _off(self):
        return "close the oxygen valve"
