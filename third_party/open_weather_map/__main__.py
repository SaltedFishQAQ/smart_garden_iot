import time
from third_party.open_weather_map.weather_adapter import WeatherAdapter


if __name__ == '__main__':
    w = WeatherAdapter()
    w.start()
    w.register_http_handler()

    try:
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        w.stop()
