from devices.biz.base_actuator import BaseActuator


class OxygenValve(BaseActuator):
    def __init__(self):
        super().__init__("oxygen valve")

    def _on(self):
        print("valve on")

    def _off(self):
        print("valve off")
