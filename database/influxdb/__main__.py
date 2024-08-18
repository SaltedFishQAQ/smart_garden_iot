import time
from database.influxdb.influxdb_adapter import InfluxdbAdapter


if __name__ == '__main__':
    i = InfluxdbAdapter()
    i.start()
    i.register_mqtt_service()
    i.register_http_handler()

    try:
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        i.stop()
