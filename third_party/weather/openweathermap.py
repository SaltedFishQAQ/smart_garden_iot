import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import time
import pytz
import paho.mqtt.client as mqtt
from constants.entity import LIGHT, IRRIGATOR

class ConfigLoader:
    def __init__(self, config_file):
        self.config_file = config_file
        self.config_data = self.load_config()

    def load_config(self):
        tree = ET.parse(self.config_file)
        root = tree.getroot()

        config_data = {
            "api_url": root.find("./weather/api_url").text,
            "api_key": root.find("./weather/api_key").text,
            "city": root.find("./weather/city").text,
            "mqtt_broker": root.find("./mqtt/broker").text,
            "mqtt_port": int(root.find("./mqtt/port").text),
            "command_channel": root.find("./mqtt/topic").text
        }
        return config_data

class WeatherService:
    def __init__(self, api_url, api_key, city, mqtt_client, command_channel):
        self.api_url = api_url
        self.api_key = api_key
        self.city = city
        self.sunrise = None
        self.sunset = None
        self.rain_probability = None
        self.mqtt_client = mqtt_client
        self.command_channel = command_channel

    def fetch_weather_data(self):
        url = f"{self.api_url}?q={self.city}&appid={self.api_key}"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            utc_sunrise = datetime.utcfromtimestamp(data['sys']['sunrise'])
            utc_sunset = datetime.utcfromtimestamp(data['sys']['sunset'])

            local_tz = pytz.timezone('Europe/Rome')
            self.sunrise = utc_sunrise.replace(tzinfo=pytz.utc).astimezone(local_tz)
            self.sunset = utc_sunset.replace(tzinfo=pytz.utc).astimezone(local_tz)

            self.rain_probability = data.get('rain', {}).get('1h', 0)
            print(f"Sunrise: {self.sunrise}, Sunset: {self.sunset}, Rain Probability: {self.rain_probability} mm")
        else:
            print(f"Error fetching data: {response.status_code} - {response.text}")

    def check_sun_times(self):
        current_time = datetime.now(pytz.timezone('Europe/Rome'))
        print(f"Current time: {current_time}")

        if current_time >= self.sunrise and current_time < self.sunset:
            self.trigger_sunrise_action()
        elif current_time >= self.sunset:
            self.trigger_sunset_action()

    def trigger_sunrise_action(self):
        print("Action Triggered: Turn off the light")
        self.mqtt_publish(self.command_channel + LIGHT, {'status': False})

    def trigger_sunset_action(self):
        print("Action Triggered: Turn on the light")
        self.mqtt_publish(self.command_channel + LIGHT, {'status': True})

    def check_rain_probability(self):
        print(f"Rain Probability Check: {self.rain_probability} mm")
        if self.rain_probability > 0:
            self.trigger_irrigator_action()

    def trigger_irrigator_action(self):
        print("Action Triggered: Close watering system")
        self.mqtt_publish(self.command_channel + IRRIGATOR, {'status': False})

    def mqtt_publish(self, topic, message):
        self.mqtt_client.publish(topic, str(message))
        print(f"Published to {topic}: {message}")

class WeatherMicroservice:
    def __init__(self, weather_service):
        self.weather_service = weather_service

    def run(self):
        self.weather_service.fetch_weather_data()
        self.weather_service.check_sun_times()

        while True:
            current_time = datetime.utcnow()
            next_sun_check = current_time + timedelta(hours=12)
            next_rain_check = current_time + timedelta(minutes=10)

            while current_time < next_sun_check:
                if current_time >= next_rain_check:
                    self.weather_service.fetch_weather_data()
                    self.weather_service.check_rain_probability()
                    next_rain_check = current_time + timedelta(minutes=10)

                time.sleep(60)
                current_time = datetime.utcnow()

            self.weather_service.fetch_weather_data()
            self.weather_service.check_sun_times()

# Load configuration from config.xml
config_loader = ConfigLoader('weather_config.xml')
config = config_loader.config_data

# MQTT setup
mqtt_client = mqtt.Client()
mqtt_client.connect(config['mqtt_broker'], config['mqtt_port'])

# Usage
weather_service = WeatherService(
    config['api_url'],
    config['api_key'],
    config['city'],
    mqtt_client,
    config['command_channel']
)
microservice = WeatherMicroservice(weather_service)

# Run the microservice
microservice.run()
