import time
from devices.thermometer import Thermometer
from devices.hygrometer import Hygrometer
from devices.light_controller import LightController


if __name__ == '__main__':
    t1 = Thermometer('temperature')
    t1.start()
    t2 = LightController('light')
    t2.start()
    t3 = Hygrometer('humidity')
    t3.start()
    try:
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        t1.stop()
        t2.stop()
        t3.stop()
