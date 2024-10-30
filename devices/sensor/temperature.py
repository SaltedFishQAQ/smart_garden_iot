import json
import random
import requests
import logging
from config_loader import load_config
from devices.biz.base_sensor import BaseSensor
# import Adafruit_DHT


class TemperatureSensor(BaseSensor):
    def __init__(self):
        super().__init__("temperature")
        # self._sensor = Adafruit_DHT.DHT11
        # self.pin = 4

        # Load the API URL and key
        self.config = load_config(data_key='temperature')

    def monitor(self) -> str:
        if not self.config or 'api_url' not in self.config or 'data_key' not in self.config:
            return json.dumps({'value': None})

        try:
            response = requests.get(self.config['api_url'])
            weather_data = response.json()
            temperature = weather_data.get(self.config['data_key'])
            if temperature is None:
                logging.error(f"Failed to fetch '{self.config['data_key']}' data from API")
                return json.dumps({
                    'value': None
                })

            random_adjustment = random.uniform(-0.5, 0.5)
            adjusted_temperature = round(temperature + random_adjustment, 2)

            return json.dumps({
                'value': adjusted_temperature
            })

        except Exception as e:
            logging.error(f"Error fetching weather data: {e}")
            return json.dumps({
                'value': None
            })

