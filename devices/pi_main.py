import time
from devices.raspberry_pi_test import RaspberryPiTest

if __name__ == '__main__':
    pi = RaspberryPiTest('pi')
    pi.start()

    try:
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        pi.stop()
