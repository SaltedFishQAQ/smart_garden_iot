import json
from devices.biz.base_device import BaseDevice
from devices.sensor.humidity import HumiditySensor


class Hygrometer(BaseDevice):
    def __init__(self, name):
        super().__init__(name)
        self.sensor = HumiditySensor()
        self.sensor.receiver = self.handle_data

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

    def handle_opt(self, opt, status):
        if self.sensor.running == status:
            return

        if status:
            self.sensor.start()
        else:
            self.sensor.stop()

    def handle_data(self, data_str):
        data = json.loads(data_str)
        if 'value' not in data:
            print("data missing humidity value, data: {}".format(data))
            return
        print(f"record data: {self.device_name}, {data}")
        self.record_data(data)
