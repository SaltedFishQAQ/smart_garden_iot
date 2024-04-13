from devices.common.base_actuator import BaseActuator


class GateControl(BaseActuator):
    def __init__(self):
        super().__init__("gate_control")

    def _on(self):
        # TODO: open the gate
        print("open the gate")

    def _off(self):
        # TODO: close the gate
        print("close the gate")
