import os
import json
import random
import requests
from devices.biz.base_sensor import BaseSensor
from common.config import ConfigLoader


TAG = "humidity"


class HumiditySensor(BaseSensor):
    def __init__(self):
        super().__init__("humidity")

        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.xml')
        self.config = ConfigLoader(config_path)

    def monitor(self) -> str:
        if self.config.root is None:
            print("API URL or data key not available in config.")
            return json.dumps({'value': None})

        try:
            url = f'{self.config.get("url")}:{self.config.get("ports/weather")}/weather/humidity'
            response = requests.get(url)

            weather_data = response.json()
            humidity = weather_data.get("humidity")

            if humidity is None:
                print(f"Failed to fetch 'humidity' data from API")
                return json.dumps({
                    'value': None
                })

            random_adjustment = random.uniform(1, 5)
            adjusted_humidity = round(min(humidity + random_adjustment, 100), 2)

            return json.dumps({
                'value': float(adjusted_humidity)
            })

        except Exception as e:
            print(f"Error fetching weather data: {e}")
            return json.dumps({
                'value': None
            })

    def measurement(self) -> str:
        return 'humidity'
