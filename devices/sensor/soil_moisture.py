import json
import requests
import logging
from config_loader import load_config
from devices.biz.base_sensor import BaseSensor
# import Adafruit_DHT


class SoilMoistureSensor(BaseSensor):
    def __init__(self, soil_type):
        super().__init__("soil_moisture")
        self.soil_type = soil_type
        # self._sensor = Adafruit_DHT.DHT11
        # self.pin = 4

        # Load the API URL and key
        self.config = load_config(data_key='soil_moisture')

    def monitor(self) -> str:
        if not self.config or 'api_url' not in self.config or 'data_key' not in self.config:
            logging.error("API URL or data key not available in config.")
            return json.dumps({'value': None})

        try:
            response = requests.get(self.config['api_url'])
            response.raise_for_status()

            soil_data = response.json()
            soil_moisture = soil_data.get(self.config['data_key'])

            # Check if soil moisture data for the given soil type
            moisture_value = soil_moisture.get(f"{self.soil_type.capitalize()} Soil")
            if moisture_value is None:
                logging.error(f"Failed to fetch moisture data for '{self.soil_type.capitalize()} Soil'")
                return json.dumps({
                    'value': None
                })

            return json.dumps({
                'value': moisture_value
            })

        except Exception as e:
            logging.error(f"Error fetching soil moisture data: {e}")
            return json.dumps({
                'value': None
            })

