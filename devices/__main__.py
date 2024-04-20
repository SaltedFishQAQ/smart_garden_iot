from devices.thermometer import Thermometer


if __name__ == '__main__':
    t = Thermometer('device1')
    t.start()

    while True:
        if input("stop running [q]:") == 'q':
            break

    t.stop()
