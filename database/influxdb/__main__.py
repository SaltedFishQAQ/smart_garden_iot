from database.influxdb.influxdb_adapter import InfluxdbAdapter


if __name__ == '__main__':
    i = InfluxdbAdapter()
    i.start()
    i.register_mqtt_service()
    i.register_http_handler()

    while True:
        if input("stop running [q]:") == 'q':
            break

    i.stop()
