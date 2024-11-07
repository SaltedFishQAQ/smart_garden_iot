import time
from devices.light_controller import LightController
from devices.oxygen_controller import OxygenController
from devices.hygrometer import Hygrometer
from devices.thermometer import Thermometer
from devices.soil_moisture_device import SoilMoistureDevice


if __name__ == '__main__':
    temperature_sensor = Thermometer('temperature')
    temperature_sensor.start()
    humidity_sensor = Hygrometer('humidity')
    humidity_sensor.start()
    light_control = LightController('light')
    light_control.start()
    oxygen_control = OxygenController('oxygen')
    oxygen_control.start()
    soil_device = SoilMoistureDevice('soil_moisture')
    soil_device.start()

    try:
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        temperature_sensor.stop()
        humidity_sensor.stop()
        light_control.stop()
        oxygen_control.stop()
        soil_device.stop()
