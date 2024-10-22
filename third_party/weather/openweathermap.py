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


class CheckWorker:
    """
    Worker responsible for fetching weather data and triggering rain alerts.
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

    def run(self):
        """
        Main method to fetch and process weather data.
        """
        self.fetch_weather_data()

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

            self.sunrise = datetime.utcfromtimestamp(data['sys']['sunrise']).replace(tzinfo=pytz.utc).astimezone(pytz.timezone(self.timezone))
            self.sunset = datetime.utcfromtimestamp(data['sys']['sunset']).replace(tzinfo=pytz.utc).astimezone(pytz.timezone(self.timezone))

            logging.info(f"Sunrise: {self.sunrise}, Sunset: {self.sunset}")

            self.rain_probability = data.get('rain', {}).get('1h', 0)
            logging.info(f"Rain Probability: {self.rain_probability} mm")

            if self.rain_probability > 0:
                self.publish_rain_prediction(data)
        else:
            logging.error(f"Error fetching data from OpenWeatherMap: {response.status_code} - {response.text}")

    def publish_rain_prediction(self, weather_data):
        """
        Publish a message to the MQTT broker indicating rain is expected and take action to stop watering.
        """
        rain_volume = weather_data.get('rain', {}).get('1h', 0)
        message = {
            "Alerts": f"Rain expected in the next hour with a volume of {rain_volume} mm."
        }
        self.mqtt_publish(self.command_channel + 'alerts', message, qos=1)
        logging.info(f"Published rain prediction: Rain expected in the next hour with {rain_volume} mm volume.")

        # Stop watering if rain is predicted
        self.mqtt_publish(self.command_channel + 'irrigator', {'type': 'opt', 'status': False}, qos=1)
        logging.info("Published to MQTT: Watering stopped due to rain prediction.")

    def mqtt_publish(self, topic, message, qos=0):
        self.mqtt_client.publish(topic, str(message), qos=qos)
        logging.info(f"Published to {topic}: {message}")


class FetchWorker:
    """
    Worker responsible for controlling lights based on sunrise/sunset times.
    """
    def __init__(self, timezone, mqtt_client, command_channel):
        self.timezone = timezone
        self.mqtt_client = mqtt_client
        self.command_channel = command_channel
        self.sunrise = None
        self.sunset = None
        self.light_on = False  # Track the state of the light (initially off)

    def run(self):
        """
        Main method to check sun events and control the lights.
        """
        self.check_sun_times()

    def update_sun_times(self, sunrise, sunset):
        """
        Update sunrise and sunset times fetched from the weather service.
        """
        self.sunrise = sunrise
        self.sunset = sunset

    def check_sun_times(self):
        """
        Check current time and trigger actions based on sunrise and sunset times.
        """
        current_time = datetime.now(pytz.timezone(self.timezone))
        logging.info(f"Current time: {current_time}")

        """
        Check if it's time to turn off/on lights at sunrise
        """
        if self.sunrise and current_time >= self.sunrise and self.light_on:
            logging.info(f"Triggering sunrise action: Turn off the lights at {self.sunrise}")
            self.trigger_sunrise_action()

        if self.sunset and current_time >= self.sunset and not self.light_on:
            logging.info(f"Triggering sunset action: Turn on the lights at {self.sunset}")
            self.trigger_sunset_action()

    def trigger_sunrise_action(self):
        """
        Trigger action to turn off the light after sunrise.
        """
        logging.info("Action Triggered: Turn off the light")
        self.mqtt_publish(self.command_channel + 'light', {'type': 'opt', 'status': False}, qos=1)
        self.light_on = False
        logging.info(f"Published to MQTT: Lights turned off at sunrise.")

    def trigger_sunset_action(self):
        """
        Trigger action to turn on the light after sunset.
        """
        logging.info("Action Triggered: Turn on the light")
        self.mqtt_publish(self.command_channel + 'light', {'type': 'opt', 'status': True}, qos=1)
        self.light_on = True  # Update the light state
        logging.info(f"Published to MQTT: Lights turned on at sunset.")

    def mqtt_publish(self, topic, message, qos=0):
        try:
            result = self.mqtt_client.publish(topic, str(message), qos=qos)
            result.wait_for_publish()
            logging.info(f"Successfully published to {topic}: {message}")
        except Exception as e:
            logging.error(f"Failed to publish to {topic}: {e}")


class WeatherMicroservice:
    """
    This class runs both the CheckWorker and FetchWorker, handling weather data fetching and light control.
    """
    def __init__(self, check_worker, fetch_worker):
        self.check_worker = check_worker
        self.fetch_worker = fetch_worker

    def run(self):
        """
        Main loop that runs both the weather data fetching and sun event handling.
        """
        next_weather_update = datetime.now(pytz.timezone(self.check_worker.timezone)) + timedelta(minutes=20)

        while True:
            current_time = datetime.now(pytz.timezone(self.check_worker.timezone))

            # Check sunrise/sunset events
            self.fetch_worker.run()

            if current_time >= next_weather_update:
                self.check_worker.run()
                next_weather_update = current_time + timedelta(minutes=20)

            time.sleep(600)


# Load configuration
config_loader = ConfigLoader('weather_config.xml')
config = config_loader.config_data

# MQTT setup
mqtt_client = mqtt.Client()
mqtt_client.connect(config['mqtt_broker'], config['mqtt_port'])
mqtt_client.loop_start()

# Initialize workers
check_worker = CheckWorker(
    config['api_url'],
    config['api_key'],
    config['city'],
    config['timezone'],
    mqtt_client,
    config['command_channel']
)

fetch_worker = FetchWorker(
    config['timezone'],
    mqtt_client,
    config['command_channel']
)

microservice = WeatherMicroservice(check_worker, fetch_worker)
microservice.run()
