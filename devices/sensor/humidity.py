import json
import random
import requests
from devices.biz.base_sensor import BaseSensor
from config_loader import load_config
# import Adafruit_DHT

class HumiditySensor(BaseSensor):
    def __init__(self):
        super().__init__("humidity")
        # self._sensor = Adafruit_DHT.DHT11
        # self.pin = 4

        self.config = load_config(data_key='humidity')

    def monitor(self) -> str:
        if not self.config or 'api_url' not in self.config or 'data_key' not in self.config:
            print("API URL or data key not available in config.")
            return json.dumps({'value': None})

        try:

            response = requests.get(self.config['api_url'])

            weather_data = response.json()
            humidity = weather_data.get(self.config['data_key'])

            if humidity is None:
                print(f"Failed to fetch '{self.config['data_key']}' data from API")
                return json.dumps({
                    'value': None
                })

            random_adjustment = random.uniform(1, 5)
            adjusted_humidity = round(min(humidity + random_adjustment, 100), 2)

            return json.dumps({
                'value': adjusted_humidity
            })

        except Exception as e:
            print(f"Error fetching weather data: {e}")
            return json.dumps({
                'value': None
            })


if __name__ == "__main__":
    temperature_sensor = HumiditySensor()
    result = temperature_sensor.monitor()
    print("Humidity sensor Data:", result)
