import json
from devices.biz.base_device import BaseDevice
from devices.actuator.light_switch import LightSwitch
from devices.sensor.light import LightSensor


class LightController(BaseDevice):
    def __init__(self, name):
        super().__init__(name)
        self.sensor = LightSensor()
        self.sensor.receiver = self.handle_data
        self.actuator = LightSwitch()

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
            self.actuator.switch(False)  # light turn off while device stop working

    def handle_opt(self, opt, status):
        if self.actuator.status != status:
            logs = self.actuator.switch(status)
            print(f"device: {self.device_name}, operation: {logs}")
            self.record_operation({
                'value': logs
            })

    def handle_data(self, data_str):
        data = json.loads(data_str)
        if 'value' not in data:
            print(f"data missing temperature value, data: {data}")
            return
        print(f"record data: {self.device_name}, {data}")
        self.record_data(data)

    def status(self):
        return {
            'device': self.working,
            'sensor': self.sensor.running,
            'actuator': self.actuator.status
        }
