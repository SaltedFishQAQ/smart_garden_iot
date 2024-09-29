import time
from devices.light_controller import LightController
from devices.oxygen_controller import OxygenController


if __name__ == '__main__':
    light_control = LightController('light')
    light_control.start()
    oxygen_control = OxygenController('oxygen')
    oxygen_control.start()

    try:
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        light_control.stop()
        oxygen_control.stop()
