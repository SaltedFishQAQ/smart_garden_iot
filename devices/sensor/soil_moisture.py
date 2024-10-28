import json
import requests
import logging
from config_loader import load_config
from devices.biz.base_sensor import BaseSensor
# import Adafruit_DHT


class SoilMoistureSensor(BaseSensor):
    def __init__(self):
        super().__init__("soil_moisture")
        # self._sensor = Adafruit_DHT.DHT11
        # self.pin = 4

        # Load the API URL and key
        self.config = load_config(data_key='soil_moisture')

    def monitor(self) -> str:
        if not self.config or 'api_url' not in self.config or 'data_key' not in self.config:
            logging.error("API URL or data key not available in config.")
            return json.dumps({'value': None})

        try:
            # Make a request to fetch soil moisture data
            response = requests.get(self.config['api_url'])
            response.raise_for_status()  # Raises an HTTPError for bad responses

            # Parse the response JSON
            soil_data = response.json()
            soil_moisture = soil_data.get(self.config['data_key'])

            if soil_moisture is None:
                logging.error(f"Failed to fetch '{self.config['data_key']}' data from API")
                return json.dumps({
                    'value': None
                })

            # Return soil moisture value
            return json.dumps({
                'value': soil_moisture
            })

        except Exception as e:
            logging.error(f"Error fetching soil moisture data: {e}")
            return json.dumps({
                'value': None
            })