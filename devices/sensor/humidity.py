from devices.common.base_sensor import BaseSensor


class HumiditySensor(BaseSensor):
    def __init__(self):
        super().__init__("humidity")

    def monitor(self) -> str:
        # TODO: Raspberry Pi get humidity interface
        return "60"
