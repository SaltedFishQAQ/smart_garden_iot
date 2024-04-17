import time
from devices.thermometer import Thermometer


if __name__ == '__main__':
    t = Thermometer('device1')
    t.start()

    while True:
        time.sleep(5)
