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
        try:
            tree = ET.parse(self.config_file)
            root = tree.getroot()

            config_data = {
                "api_url": root.find("./weather/api_url").text,
                "timezone": root.find("./weather/timezone").text,
                "mqtt_broker": root.find("./mqtt/broker").text,
                "mqtt_port": int(root.find("./mqtt/port").text),
                "mqtt_topic": root.find("./mqtt/topic").text,
            }
            logging.info(f"Configuration loaded: {config_data}")
            return config_data
        except Exception as e:
            logging.error(f"Error loading config: {e}")
            raise


class LightControlService:
    def __init__(self, weather_api_url, mqtt_broker, mqtt_port, mqtt_topic, timezone):
        self.weather_api_url = weather_api_url
        self.mqtt_broker = mqtt_broker
        self.mqtt_port = mqtt_port
        self.mqtt_topic = mqtt_topic
        self.timezone = timezone

        self.sunrise = None
        self.sunset = None
        self.light_on = False  # Track the state of the light

        self.mqtt_client = mqtt.Client()
        self.mqtt_client.connect(self.mqtt_broker, self.mqtt_port)
        self.mqtt_client.loop_start()

        self.fetch_weather_data()

    def fetch_weather_data(self):
        """
        Fetch weather data from the weather API and update sunrise and sunset times.
        """
        try:
            logging.info(f"Fetching weather data from API: {self.weather_api_url}")
            response = requests.get(self.weather_api_url, timeout=10)

            logging.info(f"API Response Status Code: {response.status_code}")
            logging.info(f"API Response Content: {response.text}")

            if response.status_code == 200:
                data = response.json()

                # Ensure that sunrise and sunset exist in the response
                if 'sunrise' not in data or 'sunset' not in data:
                    logging.error(f"Missing 'sunrise' or 'sunset' in the API response: {data}")
                    return

                logging.info(f"Raw sunrise data: {data['sunrise']}, Raw sunset data: {data['sunset']}")

                # Parse the sunrise and sunset times
                try:
                    self.sunrise = datetime.fromisoformat(data['sunrise']).astimezone(pytz.timezone(self.timezone))
                    self.sunset = datetime.fromisoformat(data['sunset']).astimezone(pytz.timezone(self.timezone))
                except Exception as e:
                    logging.error(f"Error parsing sunrise/sunset times: {e}")
                    return

                logging.info(f"Parsed Sunrise: {self.sunrise}, Parsed Sunset: {self.sunset}")
            else:
                logging.error(
                    f"Failed to fetch weather data. Status code: {response.status_code}, Response: {response.text}")
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
        Check current time and trigger actions based on sunrise/sunset times.
        """
        current_time = datetime.now(pytz.timezone(self.timezone))
        logging.info(f"Checking current time: {current_time}")

        if self.sunrise and current_time >= self.sunrise and self.light_on:
            logging.info(f"Triggering sunrise action: Turn off the lights at {self.sunrise}")
            self.trigger_sunrise_action()

        elif self.sunset and current_time >= self.sunset and not self.light_on:
            logging.info(f"Triggering sunset action: Turn on the lights at {self.sunset}")
            self.trigger_sunset_action()

        else:
            next_event = "sunset" if not self.light_on else "sunrise"
            next_event_time = self.sunset if not self.light_on else self.sunrise
            logging.info(f"Next event: {next_event} at {next_event_time}")

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
        next_weather_update = datetime.now(pytz.timezone(self.timezone)).replace(hour=0, minute=0,
                                                                                 second=0) + timedelta(days=1)

        while True:
            current_time = datetime.now(pytz.timezone(self.timezone))

            if current_time >= next_weather_update:
                self.fetch_weather_data()
                next_weather_update = current_time.replace(hour=0, minute=0, second=0) + timedelta(days=1)
                logging.info(f"Next weather update scheduled for: {next_weather_update}")

            # Check sunrise/sunset to control lights
            self.check_and_control_lights()

            # Wait minutes before checking again
            time.sleep(600)


if __name__ == '__main__':
    # Load configuration from XML
    config_loader = ConfigLoader('light_controller_config.xml')
    config = config_loader.config_data

    # Initialize and run the light control service
    light_control_service = LightControlService(
        weather_api_url=config['api_url'],
        mqtt_broker=config['mqtt_broker'],
        mqtt_port=config['mqtt_port'],
        mqtt_topic=config['mqtt_topic'],
        timezone=config['timezone']
    )
    light_control_service.run()

