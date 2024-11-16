import json
from devices.biz.base_device import BaseDevice
from devices.sensor.base import get_sensor
from devices.actuator.base import get_actuator


class Device(BaseDevice):
    def __init__(self, delegate, params):
        super().__init__(params['area_name'], params['device_name'])
        self.delegate = delegate
        items = params['items']
        if 'sensor' in items:
            self.sensor = get_sensor({
                'sensor': items['sensor'],
                'soil_type': params['soil_type'],
            })
            self.sensor.receiver = self.handle_data
        if 'actuator' in items:
            self.actuator = get_actuator({
                'actuator': items['actuator'],
                'soil_type': params['soil_type'],
            })

    def start(self):
        super().start()
        if self.sensor is not None:
            self.sensor.start()

    def stop(self):
        super().stop()
        if self.sensor is not None:
            self.sensor.stop()

    def handle_working(self, status):
        if self.sensor is not None:
            if status:
                self.sensor.start()
            else:
                self.sensor.stop()

        if self.actuator is not None and status is False:
            self.actuator.switch(False)

    def handle_opt(self, opt, status):
        if opt == 'action' and self.actuator is not None:
            if self.actuator.status != status:
                logs = self.actuator.switch(status)
                print(f"device: {self.device_name}, operation: {logs}")
                self.record_operation({
                    'value': logs
                })
        if opt == 'opt' and self.sensor is not None:
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
        self.record_data(self.sensor.measurement(), data)

    def status(self):
        result = {
            'device': self.working
        }
        if self.sensor is not None:
            result['sensor'] = self.sensor.running
        if self.actuator is not None:
            result['actuator'] = self.actuator.status

        return result
