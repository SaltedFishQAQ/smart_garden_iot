import json
from devices.biz.base_device import BaseDevice
from devices.actuator.light_switch import LightSwitch


class LightController(BaseDevice):
    def __init__(self, name):
        self.conf = json.load(open('./configuration.json'))
        super().__init__(name, self.conf['broker'], self.conf['port'])
        self.actuator = LightSwitch()

    def handle_working(self, status):
        if status is False:  # light turn off while device stop working
            self.actuator.switch(False)

    def handle_opt(self, opt, status):
        self.actuator.switch(status)
        print(f"device: {self.device_name}, current light switch {self.actuator.get_status()}")
