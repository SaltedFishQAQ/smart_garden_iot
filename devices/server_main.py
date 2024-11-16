import time
from devices.area.area import AreaController


if __name__ == '__main__':
    c = AreaController()

    try:
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        c.stop()
