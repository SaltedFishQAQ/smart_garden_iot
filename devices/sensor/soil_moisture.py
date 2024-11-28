import os
import json
import requests
import logging
from common.config import ConfigLoader
from devices.biz.base_sensor import BaseSensor


TAG = "soil_moisture"


class SoilMoistureSensor(BaseSensor):
    def __init__(self, soil_type):
        super().__init__("soil_moisture")
        self.soil_type = soil_type

        # Load the API URL and key
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.xml')
        self.config = ConfigLoader(config_path)

    def monitor(self) -> str:
        if self.config.root is None:
            logging.error("API URL or data key not available in config.")
            return json.dumps({'value': None})

        try:
            url = f'{self.config.get("url")}:{self.config.get("ports/soil_moisture_sensor")}/soil_moisture'
            response = requests.get(url)
            response.raise_for_status()

            soil_data = response.json()
            soil_moisture = soil_data.get('soil_moisture')

            # Check if soil moisture data for the given soil type
            moisture_value = soil_moisture.get(f"{self.soil_type.capitalize()} Soil")
            if moisture_value is None:
                logging.error(f"Failed to fetch moisture data for '{self.soil_type.capitalize()} Soil'")
                return json.dumps({
                    'value': None
                })

            return json.dumps({
                'value': float(moisture_value)
            })

        except Exception as e:
            logging.error(f"Error fetching soil moisture data: {e}")
            return json.dumps({
                'value': None
            })

    def measurement(self) -> str:
        return 'soil'

