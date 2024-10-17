import logging
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import time
import pytz
import paho.mqtt.client as mqtt

# Configure logging
logging.basicConfig(
    filename='/tmp/weather.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Override the formatter to use local time instead of UTC
logging.Formatter.converter = time.localtime


class ConfigLoader:
    """
    This class loads configuration from an XML file.
    """

    def __init__(self, config_file):
        self.config_file = config_file
        self.config_data = self.load_config()

    def load_config(self):
        """
        Parse the XML config file and return configuration data as a dictionary.
        """
        tree = ET.parse(self.config_file)
        root = tree.getroot()

        config_data = {
            "api_url": root.find("./weather/api_url").text,
            "api_key": root.find("./weather/api_key").text,
            "city": root.find("./weather/city").text,
            "timezone": root.find("./weather/timezone").text,
            "mqtt_broker": root.find("./mqtt/broker").text,
            "mqtt_port": int(root.find("./mqtt/port").text),
            "command_channel": root.find("./mqtt/topic").text
        }
        return config_data


class WeatherService:
    """
    Fetching weather data from the API and checking rain probability.
    """

    def __init__(self, api_url, api_key, city, timezone, mqtt_client, command_channel):
        self.api_url = api_url
        self.api_key = api_key
        self.city = city
        self.timezone = timezone
        self.mqtt_client = mqtt_client
        self.command_channel = command_channel
        self.sunrise = None
        self.sunset = None
        self.rain_probability = None

    def fetch_weather_data(self):
        """
        Fetch weather data from the OpenWeatherMap API and check rain probability.
        """
        url = f"{self.api_url}?q={self.city}&appid={self.api_key}"

        logging.info(f"Calling OpenWeatherMap API: {url}")

        response = requests.get(url, timeout=10)

        logging.info(f"Received response from OpenWeatherMap API: {response.status_code}")

        if response.status_code == 200:
            data = response.json()

            utc_sunrise = datetime.utcfromtimestamp(data['sys']['sunrise'])
            utc_sunset = datetime.utcfromtimestamp(data['sys']['sunset'])

            local_tz = pytz.timezone(self.timezone)
            self.sunrise = utc_sunrise.replace(tzinfo=pytz.utc).astimezone(local_tz)
            self.sunset = utc_sunset.replace(tzinfo=pytz.utc).astimezone(local_tz)

            logging.info(f"Sunrise: {self.sunrise}, Sunset: {self.sunset}")

            current_time = datetime.now(pytz.timezone(self.timezone))
            if current_time < self.sunrise:
                logging.info(f"Lights will turn off at sunrise: {self.sunrise}")
            elif current_time < self.sunset:
                logging.info(f"Lights will turn on at sunset: {self.sunset}")
            else:
                logging.info(f"Lights are already on after sunset.")

            self.rain_probability = data.get('rain', {}).get('1h', 0)
            logging.info(f"Rain Probability: {self.rain_probability} mm")

            # Publish rain information if there's rain in the next hour
            if self.rain_probability > 0:
                self.publish_rain_prediction(data)
        else:
            logging.error(f"Error fetching data from OpenWeatherMap: {response.status_code} - {response.text}")

    def publish_rain_prediction(self, weather_data):
        """
        Publish a message to the MQTT broker indicating rain is expected.
        """
        rain_volume = weather_data.get('rain', {}).get('1h', 0)
        message = {
            "prediction": f"Rain expected in the next hour with a volume of {rain_volume} mm."
        }
        self.mqtt_publish(self.command_channel + 'prediction', message, qos=1)

        logging.info(f"Published rain prediction: Rain expected in the next hour with {rain_volume} mm volume.")

    def mqtt_publish(self, topic, message, qos=0):
        """
        Publish a message to the MQTT broker.
        """
        self.mqtt_client.publish(topic, str(message), qos=qos)
        logging.info(f"Published to {topic}: {message}")


class SunEventService:
    """
    This class is responsible for checking sunrise/sunset times and controlling lights accordingly.
    """

    def __init__(self, sunrise, sunset, timezone, mqtt_client, command_channel):
        self.sunrise = sunrise
        self.sunset = sunset
        self.timezone = timezone
        self.mqtt_client = mqtt_client
        self.command_channel = command_channel
        self.light_on = False  # Track the state of the light (initially off)

    def check_sun_times(self):
        """
        Check current time and trigger actions based on sunrise and sunset times.
        """
        current_time = datetime.now(pytz.timezone(self.timezone))
        logging.info(f"Current time: {current_time}")

        # Turn off lights if after sunrise but before sunset
        if current_time >= self.sunrise and current_time < self.sunset:
            if self.light_on:  # Only turn off if the light is on
                logging.info(f"Light state before sunrise action: {self.light_on}")
                self.trigger_sunrise_action()

        # Turn on lights if after sunset
        elif current_time >= self.sunset:
            if not self.light_on:  # Only turn on if the light is off
                logging.info(f"Light state before sunset action: {self.light_on}")
                self.trigger_sunset_action()

    def trigger_sunrise_action(self):
        """
        Trigger action to turn off the light after sunrise.
        """
        logging.info("Action Triggered: Turn off the light")
        self.mqtt_publish(self.command_channel + 'light', {'type': 'opt', 'status': False}, qos=1)
        self.light_on = False  # Update the light state
        logging.info(f"Light state after sunrise action: {self.light_on}")
        logging.info("Published to MQTT: Lights turned off at sunrise.")

    def trigger_sunset_action(self):
        """
        Trigger action to turn on the light after sunset.
        """
        logging.info("Action Triggered: Turn on the light")
        self.mqtt_publish(self.command_channel + 'light', {'type': 'opt', 'status': True}, qos=1)
        self.light_on = True  # Update the light state
        logging.info(f"Light state after sunset action: {self.light_on}")
        logging.info("Published to MQTT: Lights turned on at sunset.")

    def mqtt_publish(self, topic, message, qos=0):
        """
        Publish a message to the MQTT broker.
        """
        self.mqtt_client.publish(topic, str(message), qos=qos)
        logging.info(f"Published to {topic}: {message}")



class WeatherMicroservice:
    """
    This class runs both the WeatherService and SunEventService, handling both weather checks and light control.
    """

    def __init__(self, weather_service, sun_event_service):
        self.weather_service = weather_service
        self.sun_event_service = sun_event_service

    def run(self):
        """
        Main loop that runs both the weather data fetching and sun event handling.
        """
        next_weather_update = datetime.now(pytz.timezone(self.weather_service.timezone)) + timedelta(minutes=20)

        while True:
            current_time = datetime.now(pytz.timezone(self.weather_service.timezone))

            # Check sunrise/sunset events
            self.sun_event_service.check_sun_times()

            if current_time >= next_weather_update:
                self.weather_service.fetch_weather_data()
                next_weather_update = current_time + timedelta(minutes=20)  # Schedule next fetch

            time.sleep(600)


# Load configuration
config_loader = ConfigLoader('weather_config.xml')
config = config_loader.config_data

# MQTT setup
mqtt_client = mqtt.Client()
mqtt_client.connect(config['mqtt_broker'], config['mqtt_port'])

weather_service = WeatherService(
    config['api_url'],
    config['api_key'],
    config['city'],
    config['timezone'],
    mqtt_client,
    config['command_channel']
)
weather_service.fetch_weather_data()

sun_event_service = SunEventService(
    weather_service.sunrise,  # Use the fetched sunrise time
    weather_service.sunset,  # Use the fetched sunset time
    config['timezone'],
    mqtt_client,
    config['command_channel']
)

microservice = WeatherMicroservice(weather_service, sun_event_service)
microservice.run()


