import threading

from devices.thermometer import Thermometer
from database.influxdb.influxdb_adapter import InfluxdbAdapter


def thread1():
    i = InfluxdbAdapter()
    i.start()
    i.register_mqtt_service()


def thread2():
    t = Thermometer('device1')
    t.start()


if __name__ == '__main__':
    t1 = threading.Thread(target=thread1())
    t2 = threading.Thread(target=thread2())
    t1.start()
    t2.start()
    t1.join()
    t2.join()

