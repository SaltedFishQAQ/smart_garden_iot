import os
import time
from devices.area.device import Device
from common.config import ConfigLoader


class Area:
    def __init__(self, params):
        self.name = params['area_name']
        self.soil_type = params['soil_type']
        self.device_list = []
        for device_name in params['devices']:
            d = Device(self, {
                'area_name': self.name,
                'soil_type': self.soil_type,
                'device_name': device_name,
                'items': params['devices'][device_name]
            })
            d.start()
            self.device_list.append(d)

    def stop(self):
        for device in self.device_list:
            device.stop()


class AreaController:
    def __init__(self):
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.xml')
        config = ConfigLoader(config_path).json()
        self.area_list = []
        for name in config['area']:
            if name not in config:
                continue
            a = Area({
                'area_name': name,
                'soil_type': config['area'][name]['soil_type'],
                'devices': config[name]
            })
            self.area_list.append(a)

    def stop(self):
        for area in self.area_list:
            area.stop()


if __name__ == '__main__':
    c = AreaController()

    try:
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        c.stop()
