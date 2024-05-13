from devices.thermometer import Thermometer
from devices.hygrometer import Hygrometer
from devices.light_controller import LightController


if __name__ == '__main__':
    t1 = Thermometer('temperature')
    t1.start()
    t2 = LightController('light')
    t2.start()
    t2.register_mqtt_service()
    t3 = Hygrometer('humidity')
    t3.start()

    while True:
        if input("stop running [q]:") == 'q':
            break

    t1.stop()
    t2.stop()
