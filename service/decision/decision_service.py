import os
import requests
import logging
import time
import pytz
import constants.entity
import message_broker.channels as mb_channel
from datetime import datetime, timedelta
from common.config import ConfigLoader
from common.base_service import BaseService
from service.decision.controller.light import LightController

logging.basicConfig(
    filename='/tmp/light_controller.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


class DecisionService(BaseService):
    def __init__(self):
        super().__init__(constants.entity.DECISION_SERVICE)
        self.control_groups = []
        self.command_channel = mb_channel.DEVICE_COMMAND
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'light_controller.xml')
        config = ConfigLoader(config_path)

        self.weather_api_url = config.get("./weather/api_url")
        self.mqtt_broker = config.get("./mqtt/broker")
        self.mqtt_port = config.get("./mqtt/port")
        self.mqtt_topic = config.get("./mqtt/topic")
        self.timezone = config.get("./weather/timezone")

    def start(self):
        super().start()
        self.init_mqtt_client()

    def stop(self):
        self.remove_mqtt_client()

    def fetch_weather_data(self):
        """
        Fetch weather data from the weather API and update sunrise and sunset times.
        """
        try:
            logging.info(f"Fetching weather data from API: {self.weather_api_url}")
            response = requests.get(self.weather_api_url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                for group in self.control_groups:
                    group.handle_data(data)
            else:
                logging.error(f"Failed to fetch weather data. Status code: {response.status_code}")
        except Exception as e:
            logging.error(f"Error fetching weather data: {e}")

    def run(self):
        """
        Main loop that fetches weather data once a day and checks for light control every 10 minutes.
        """
        self.fetch_weather_data()

        next_weather_update = datetime.now(pytz.timezone(self.timezone)).replace(hour=0, minute=0, second=0) + timedelta(days=1)

        while True:
            current_time = datetime.now(pytz.timezone(self.timezone))

            if current_time >= next_weather_update:
                self.fetch_weather_data()
                next_weather_update = current_time.replace(hour=0, minute=0, second=0) + timedelta(days=1)

            for group in self.control_groups:
                group.handle_check()

            # check loop
            time.sleep(600)

    def register_controller(self):
        self.control_groups = [
            LightController(self)
        ]
