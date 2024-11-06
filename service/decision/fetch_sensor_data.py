import json
import requests
import random
import logging
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET

# Load configuration from XML file
def load_config(file_path='config.xml', data_key=None):
    config = {}
    tree = ET.parse(file_path)
    root = tree.getroot()

    base_url = root.find('url').text

    if data_key == 'temperature' or data_key == 'humidity':
        port = root.find('ports/weather').text
    elif data_key == 'soil_moisture':
        port = root.find('ports/soil_moisture_sensor').text
    else:
        logging.error("Invalid data_key provided, must be 'temperature', 'humidity', or 'soil_moisture'.")
        return None

    data_path = root.find(f'data_keys/{data_key}').text

    # Construct the full API URL
    config['api_url'] = f"{base_url}:{port}/{data_path}"
    config['data_key'] = data_key

    return config

# Base sensor class
class BaseSensor:
    def __init__(self, sensor_type):
        self.sensor_type = sensor_type

# Temperature sensor with API access
class TemperatureSensor(BaseSensor):
    def __init__(self):
        super().__init__("temperature")
        self.config = load_config(data_key='temperature')

    def monitor(self) -> str:
        if not self.config or 'api_url' not in self.config or 'data_key' not in self.config:
            return json.dumps({'temperature': None})

        try:
            response = requests.get(self.config['api_url'])
            weather_data = response.json()
            temperature = weather_data.get(self.config['data_key'])
            if temperature is None:
                logging.error(f"Failed to fetch '{self.config['data_key']}' data from API")
                return json.dumps({'temperature': None})

            random_adjustment = random.uniform(-0.5, 0.5)
            adjusted_temperature = round(temperature + random_adjustment, 2)

            return json.dumps({'temperature': adjusted_temperature})

        except Exception as e:
            logging.error(f"Error fetching weather data: {e}")
            return json.dumps({'temperature': None})

# Humidity sensor with API access
class HumiditySensor(BaseSensor):
    def __init__(self):
        super().__init__("humidity")
        self.config = load_config(data_key='humidity')

    def monitor(self) -> str:
        if not self.config or 'api_url' not in self.config or 'data_key' not in self.config:
            print("API URL or data key not available in config.")
            return json.dumps({'humidity': None})

        try:
            response = requests.get(self.config['api_url'])
            weather_data = response.json()
            humidity = weather_data.get(self.config['data_key'])

            if humidity is None:
                print(f"Failed to fetch '{self.config['data_key']}' data from API")
                return json.dumps({'humidity': None})

            random_adjustment = random.uniform(1, 5)
            adjusted_humidity = round(min(humidity + random_adjustment, 100), 2)

            return json.dumps({'humidity': adjusted_humidity})

        except Exception as e:
            print(f"Error fetching weather data: {e}")
            return json.dumps({'humidity': None})

# Soil Moisture sensor with API access
class SoilMoistureSensor(BaseSensor):
    def __init__(self, soil_type):
        super().__init__("soil_moisture")
        self.soil_type = soil_type
        self.config = load_config(data_key='soil_moisture')

    def monitor(self) -> str:
        if not self.config or 'api_url' not in self.config or 'data_key' not in self.config:
            logging.error("API URL or data key not available in config.")
            return json.dumps({'soil_moisture': None})

        try:
            response = requests.get(self.config['api_url'])
            response.raise_for_status()

            soil_data = response.json()
            soil_moisture = soil_data.get(self.config['data_key'])

            # Check if soil moisture data for the given soil type
            moisture_value = soil_moisture.get(f"{self.soil_type.capitalize()} Soil")
            if moisture_value is None:
                logging.error(f"Failed to fetch moisture data for '{self.soil_type.capitalize()} Soil'")
                return json.dumps({'soil_moisture': None})

            return json.dumps({'soil_moisture': moisture_value})

        except Exception as e:
            logging.error(f"Error fetching soil moisture data: {e}")
            return json.dumps({'soil_moisture': None})

## DATABASE ##
'''
class SensorDataFetcher:
    def __init__(self, influx_url, default_hours=1):
        self.influx_url = influx_url
        self.default_hours = default_hours

    def fetch_data(self, measurement, hours=None):
        if hours is None:
            hours = self.default_hours

        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours)

        params = {
            "measurement": measurement,
            "start_at": start_time.strftime("%Y-%m-%d %H:%M:%S"),
            "stop_at": end_time.strftime("%Y-%m-%d %H:%M:%S"),
            "page": 1,
            "size": 1
        }

        response = requests.get(self.influx_url, params=params)

        if response.status_code == 200:
            data = response.json().get('list', [])
            return data
        else:
            print(f"Failed to fetch {measurement} data:", response.status_code, response.text)
            return None
'''


temperature_sensor = TemperatureSensor()
humidity_sensor = HumiditySensor()
soil_moisture_sensor = SoilMoistureSensor(soil_type='Sandy')

temperature_data = temperature_sensor.monitor()
humidity_data = humidity_sensor.monitor()
soil_moisture_data = soil_moisture_sensor.monitor()

print(temperature_data)
print(humidity_data)
print(soil_moisture_data)

'''
# Example usage for InfluxDB data fetching (commented out)

fetcher = SensorDataFetcher("http://43.131.48.203:8084/influx/data")

# Fetch data for each type
humidity_data = fetcher.fetch_data("humidity")
temperature_data = fetcher.fetch_data("temperature")
soil_moisture_data = fetcher.fetch_data("soil_moisture")

print(humidity_data, temperature_data, soil_moisture_data)

'''