import json
from devices.biz.base_device import BaseDevice
from devices.actuator.oxygen_valve import OxygenValve
from devices.sensor.gas import GasDetector


class OxygenController(BaseDevice):
    def __init__(self, name):
        self.conf = json.load(open('./configuration.json'))
        super().__init__(name, self.conf['broker'], self.conf['port'])
        self.sensor = GasDetector()
        self.sensor.receiver = self.handle_data
        self.actuator = OxygenValve()

    def start(self):
        super().start()
        self.sensor.start()

    def stop(self):
        super().stop()
        self.sensor.stop()

    def handle_working(self, status):
        if status:
            self.sensor.start()
        else:
            self.sensor.stop()
            self.actuator.switch(False)

    def handle_opt(self, opt, status):
        if self.actuator.status != status:
            self.actuator.switch(status)
            print(f"device: {self.device_name}, current light switch {self.actuator.display_status()}")

    def handle_data(self, data_str):
        data = json.loads(data_str)
        if 'value' not in data:
            print(f"data missing temperature value, data: {data}")
            return

        self.record_data(data)
