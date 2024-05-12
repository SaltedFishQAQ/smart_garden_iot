from devices.thermometer import Thermometer
from devices.light_controller import LightController


if __name__ == '__main__':
    t1 = Thermometer('device1')
    t1.start()
    t2 = LightController('light')
    t2.start()
    t2.register_mqtt_service()

    while True:
        if input("stop running [q]:") == 'q':
            break

    t1.stop()
    t2.stop()
