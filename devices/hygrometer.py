import json
from devices.biz.base_device import BaseDevice
from devices.sensor.humidity import HumiditySensor


class Hygrometer(BaseDevice):
    def __init__(self, name):
        self.conf = json.load(open('./configuration.json'))
        super().__init__(name, self.conf['broker'], self.conf['port'])
        self.sensor = HumiditySensor()
        self.sensor.receiver = self.handle_data

    def start(self):
        super().start()
        self.sensor.start()

    def stop(self):
        super().stop()
        self.sensor.stop()

    def handle_working(self, status):
        if status is False:
            self.sensor.stop()

    def handle_opt(self, opt, status):
        if status:
            self.sensor.start()
        else:
            self.sensor.stop()

    def handle_data(self, data_str):
        data = json.loads(data_str)
        if 'value' not in data:
            print("data missing humidity value, data: {}".format(data))
            return

        self.record_data(data)
