import requests
import logging
import time
import paho.mqtt.client as mqtt
from datetime import datetime, timedelta
import pytz
import xml.etree.ElementTree as ET

logging.basicConfig(
    filename='/tmp/light_controller.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

class ConfigLoader:
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
            "timezone": root.find("./weather/timezone").text,
            "mqtt_broker": root.find("./mqtt/broker").text,
            "mqtt_port": int(root.find("./mqtt/port").text),
            "mqtt_topic": root.find("./mqtt/topic").text,
        }
        return config_data

class LightControlService:
    def __init__(self, weather_api_url, mqtt_broker, mqtt_port, mqtt_topic, timezone):
        self.weather_api_url = weather_api_url
        self.mqtt_broker = mqtt_broker
        self.mqtt_port = mqtt_port
        self.mqtt_topic = mqtt_topic
        self.timezone = timezone

        self.sunrise = None
        self.sunset = None
        self.light_on = False

        # Track actions
        self.sunrise_triggered = False
        self.sunset_triggered = False

        self.mqtt_client = mqtt.Client()
        self.mqtt_client.connect(self.mqtt_broker, self.mqtt_port)
        self.mqtt_client.loop_start()

    def fetch_weather_data(self):
        """
        Fetch weather data from the weather API and update sunrise and sunset times.
        """
        try:
            logging.info(f"Fetching weather data from API: {self.weather_api_url}")
            response = requests.get(self.weather_api_url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.sunrise = datetime.fromisoformat(data['sunrise']).astimezone(pytz.timezone(self.timezone))
                self.sunset = datetime.fromisoformat(data['sunset']).astimezone(pytz.timezone(self.timezone))
                logging.info(f"Updated sunrise: {self.sunrise}, sunset: {self.sunset}")
            else:
                logging.error(f"Failed to fetch weather data. Status code: {response.status_code}")
        except Exception as e:
            logging.error(f"Error fetching weather data: {e}")

    def mqtt_publish(self, topic, message, qos=1):
        """
        Publish an MQTT message.
        """
        try:
            self.mqtt_client.publish(topic, str(message), qos=qos)
            logging.info(f"Published to {topic}: {message}")
        except Exception as e:
            logging.error(f"Failed to publish to {topic}: {e}")

    def check_and_control_lights(self):
        """
        Logic section --
        Check current time and trigger actions based on sunrise/sunset times.
        """
        current_time = datetime.now(pytz.timezone(self.timezone))
        logging.info(f"Checking current time: {current_time}")


        # Check if sunrise has passed and if the sunrise action hasn't been triggered today
        if self.sunrise and current_time >= self.sunrise and not self.sunrise_triggered:
            logging.info(f"Triggering sunrise action: Turn off the lights at {self.sunrise}")
            self.trigger_sunrise_action()
            self.sunrise_triggered = True  # Set sunrise as triggered
            self.sunset_triggered = False  # Reset sunset trigger for the next sunset

        # Check if sunset has passed and if the sunset action hasn't been triggered today
        elif self.sunset and current_time >= self.sunset and not self.sunset_triggered:
            logging.info(f"Triggering sunset action: Turn on the lights at {self.sunset}")
            self.trigger_sunset_action()
            self.sunset_triggered = True  # Set sunset as triggered
            self.sunrise_triggered = False  # Reset sunrise trigger for the next sunrise

        # Midnight reset triggers
        if current_time.hour == 0 and current_time.minute == 0:
            self.sunrise_triggered = False
            self.sunset_triggered = False

    def trigger_sunrise_action(self):
        """
        Turn off the light after sunrise.
        """
        logging.info("Action: Turning off the light")
        self.mqtt_publish(self.mqtt_topic + 'light', {'type': 'opt', 'status': False}, qos=1)
        self.light_on = False
        logging.info("Published MQTT message to turn off the lights.")

    def trigger_sunset_action(self):
        """
        Turn on the light after sunset.
        """
        logging.info("Action: Turning on the light")
        self.mqtt_publish(self.mqtt_topic + 'light', {'type': 'opt', 'status': True}, qos=1)
        self.light_on = True
        logging.info("Published MQTT message to turn on the lights.")

    def run(self):
        """
        Main loop that fetches weather data once a day and checks for light control every 10 minutes.
        """
        self.fetch_weather_data()

        next_weather_update = datetime.now(pytz.timezone(self.timezone)).replace(hour=0, minute=0, second=0) + timedelta(days=1)

        while True:
            current_time = datetime.now(pytz.timezone(self.timezone))

            #Update sunrise / sunset time daily
            if current_time >= next_weather_update:
                self.fetch_weather_data()
                next_weather_update = current_time.replace(hour=0, minute=0, second=0) + timedelta(days=1)

            self.check_and_control_lights()

            # check loop
            time.sleep(600)

if __name__ == '__main__':
    # Load configuration
    config_loader = ConfigLoader('light_controller.xml')
    config = config_loader.config_data

    light_control_service = LightControlService(
        weather_api_url=config['api_url'],
        mqtt_broker=config['mqtt_broker'],
        mqtt_port=config['mqtt_port'],
        mqtt_topic=config['mqtt_topic'],
        timezone=config['timezone']
    )
    light_control_service.run()

