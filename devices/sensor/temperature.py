import os
import json
import random
import requests
import logging
from common.config import ConfigLoader
from devices.biz.base_sensor import BaseSensor


TAG = "temperature"


class TemperatureSensor(BaseSensor):
    def __init__(self):
        super().__init__("temperature")

        # Load the API URL and key
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.xml')
        self.config = ConfigLoader(config_path)

    def monitor(self) -> str:
        if self.config.root is None:
            return json.dumps({'value': None})

        try:
            url = f'{self.config.get("url")}:{self.config.get("ports/weather")}/weather/temperature'
            response = requests.get(url)
            weather_data = response.json()
            temperature = weather_data.get('temperature')
            if temperature is None:
                logging.error(f"Failed to fetch 'temperature' data from API")
                return json.dumps({
                    'value': None
                })

            random_adjustment = random.uniform(-0.5, 0.5)
            adjusted_temperature = round(temperature + random_adjustment, 2)

            return json.dumps({
                'value': float(adjusted_temperature)
            })

        except Exception as e:
            logging.error(f"Error fetching weather data: {e}")
            return json.dumps({
                'value': None
            })

    def measurement(self) -> str:
        return 'temperature'
