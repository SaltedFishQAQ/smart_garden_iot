import json
import pytz
from common.log import Logger
from datetime import datetime
from service.decision.controller.base import BaseController


class LightController(BaseController):
    def __init__(self, delegate):
        self.delegate = delegate
        self.logger = Logger(prefix=f'light controller:')
        # flag
        self.sunrise = None
        self.sunset = None
        self.light_on = False
        # Track actions
        self.sunrise_triggered = False
        self.sunset_triggered = False

    def handle_data(self, data):
        """
        Fetch weather data from the weather API and update sunrise and sunset times.
        """
        self.sunrise = datetime.fromisoformat(data['sunrise']).astimezone(pytz.timezone(self.delegate.timezone))
        self.sunset = datetime.fromisoformat(data['sunset']).astimezone(pytz.timezone(self.delegate.timezone))

    def handle_check(self):
        """
        Logic section --
        Check current time and trigger actions based on sunrise/sunset times.
        """
        current_time = datetime.now(pytz.timezone(self.delegate.timezone))

        # Check if sunrise has passed and if the sunrise action hasn't been triggered today
        if self.sunrise and current_time >= self.sunrise and not self.sunrise_triggered:
            self.logger.info(f"Triggering sunrise action: Turn off the lights at {self.sunrise}")
            self.trigger_sunrise_action()
            self.sunrise_triggered = True  # Set sunrise as triggered
            self.sunset_triggered = False  # Reset sunset trigger for the next sunset

        # Check if sunset has passed and if the sunset action hasn't been triggered today
        elif self.sunset and current_time >= self.sunset and not self.sunset_triggered:
            self.logger.info(f"Triggering sunset action: Turn on the lights at {self.sunset}")
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
        self.delegate.mqtt_publish(self.delegate.command_channel + 'light', json.dumps({"type": "opt", "status": False}))
        self.light_on = False

    def trigger_sunset_action(self):
        """
        Turn on the light after sunset.
        """
        self.delegate.mqtt_publish(self.delegate.command_channel + 'light', json.dumps({"type": "opt", "status": True}))
        self.light_on = True
