import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import time
import os
import pytz
import paho.mqtt.client as mqtt
from constants.entity import LIGHT, IRRIGATOR


class ConfigLoader:
    def __init__(self, config_file):
        self.config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), config_file)
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
            "command_channel": root.find("./mqtt/topic").text,
            "timezone": root.find("./weather/timezone").text,
        }
        return config_data


class WeatherService:
    def __init__(self, api_url, api_key, city,timezone, mqtt_client, command_channel):
        self.api_url = api_url
        self.api_key = api_key
        self.city = city
        self.timezone = timezone
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

            local_tz = pytz.timezone(self.timezone)
            self.sunrise = utc_sunrise.replace(tzinfo=pytz.utc).astimezone(local_tz)
            self.sunset = utc_sunset.replace(tzinfo=pytz.utc).astimezone(local_tz)

            self.rain_probability = data.get('rain', {}).get('1h', 0)
            print(f"Sunrise: {self.sunrise}, Sunset: {self.sunset}, Rain Probability: {self.rain_probability} mm")

            #publish rain information
            if self.rain_probability >= 0:
                self.publish_rain_prediction(data)
        else:
            print(f"Error fetching data: {response.status_code} - {response.text}")

    def publish_rain_prediction(self, weather_data):
        # Extract rain prediction details
        rain_volume = weather_data.get('rain', {}).get('1h', 0)
        message = {
            "prediction": f"Rain expected in the next hour with a volume of {rain_volume} mm."
        }
        self.mqtt_publish(self.command_channel + 'prediction', message)

    def check_sun_times(self):
        current_time = datetime.now(pytz.timezone(self.timezone))
        print(f"Current time: {current_time}")

        if self.sunrise <= current_time < self.sunset:
            self.trigger_sunrise_action()
        elif current_time >= self.sunset:
            self.trigger_sunset_action()

    def trigger_sunrise_action(self):
        print("Action Triggered: Turn off the light")
        self.mqtt_publish(self.command_channel + LIGHT, {"type": "opt",'status': False})

    def trigger_sunset_action(self):
        print("Action Triggered: Turn on the light")
        self.mqtt_publish(self.command_channel + LIGHT, {"type": "opt",'status': True})

    def check_rain_probability(self):
        print(f"Rain Probability Check: {self.rain_probability} mm")
        if self.rain_probability > 0:
            self.trigger_irrigator_action()

    def trigger_irrigator_action(self):
        print("Action Triggered: Close watering system")
        self.mqtt_publish(self.command_channel + IRRIGATOR, {"type": "opt",'status': False})

    def mqtt_publish(self, topic, message):
        self.mqtt_client.publish(topic, str(message))
        print(f"Published to {topic}: {message}")


class WeatherMicroservice:
    def __init__(self, weather_service):
        self.weather_service = weather_service

    def run(self):
        while True:
            # fetch data
            self.weather_service.fetch_weather_data()
            self.weather_service.check_sun_times()

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


class WeatherMicroservice:
    def __init__(self, weather_service):
        self.weather_service = weather_service

    def run(self):
        # Fetch initial weather data and update sunrise/sunset times
        self.weather_service.fetch_weather_data()
        self.weather_service.check_sun_times()

        while True:
            current_time = datetime.now(pytz.timezone(self.weather_service.timezone))

            # Calculate next sunrise/sunset check times based on current sunrise/sunset
            next_sunrise_check = self.weather_service.sunrise - timedelta(minutes=30)
            next_sunset_check = self.weather_service.sunset - timedelta(minutes=30)

            # Re-fetch weather data every 12 hours to update sunrise/sunset times
            next_weather_update = current_time + timedelta(hours=12)

            while current_time < next_weather_update:
                # Check if it's time to refetch the weather data for new sunrise/sunset times
                if current_time >= next_sunrise_check or current_time >= next_sunset_check:
                    # Refetch weather data 30 minutes before the next sunrise or sunset
                    self.weather_service.fetch_weather_data()
                    self.weather_service.check_sun_times()

                    # Recalculate the next check times based on updated sunrise/sunset times
                    next_sunrise_check = self.weather_service.sunrise - timedelta(minutes=30)
                    next_sunset_check = self.weather_service.sunset - timedelta(minutes=30)
                    next_weather_update = current_time + timedelta(hours=12)

                # Sleep for 10 minutes before the next check
                time.sleep(600)  # 10 minutes
                current_time = datetime.now(pytz.timezone(self.weather_service.timezone))


if __name__ == '__main__':
    # Load configuration
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
        config['timezone'],
        mqtt_client,
        config['command_channel']
    )
    microservice = WeatherMicroservice(weather_service)

    microservice.run()
