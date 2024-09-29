import time
from devices.light_controller import LightController


if __name__ == '__main__':
    c = LightController('light')
    c.start()

    try:
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        c.stop()
