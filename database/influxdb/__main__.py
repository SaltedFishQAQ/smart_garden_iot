import time
from database.influxdb.influxdb_adapter import InfluxdbAdapter


if __name__ == '__main__':
    i = InfluxdbAdapter()
    i.start()
    i.register_mqtt_service()

    while True:
        time.sleep(5)
