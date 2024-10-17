from gpiozero import LED
from devices.biz.base_actuator import BaseActuator


class LightSwitchPi(BaseActuator):
    def __init__(self):
        super().__init__("light switch pi")
        self.led = LED(16)
        self.pin = 17

    def _on(self):
        self.led.on()
        return "turn on the light"

    def _off(self):
        self.led.off()
        return "turn off the light"
