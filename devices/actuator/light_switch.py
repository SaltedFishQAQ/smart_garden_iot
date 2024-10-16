# import RPi.GPIO as GPIO
from devices.biz.base_actuator import BaseActuator


class LightSwitch(BaseActuator):
    def __init__(self):
        super().__init__("light switch")
        # GPIO.setmode(GPIO.BCM)
        # self.pin = 17
        # GPIO.setup(self.pin, GPIO.OUT)

    def _on(self):
        # GPIO.output(self.pin, GPIO.HIGH)
        return "turn on the light"

    def _off(self):
        # GPIO.output(self.pin, GPIO.LOW)
        return "turn off the light"
