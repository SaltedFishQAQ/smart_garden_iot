import time
import json
import requests
import threading
import logging
import constants.entity
import constants.http as const_h
from common.base_service import BaseService
import message_broker.channels as mb_channel

# Set up logging configuration
logging.basicConfig(level=logging.INFO)


class ScheduleService(BaseService):
    def __init__(self):
        super().__init__(constants.entity.SCHEDULE_SERVICE)
        self.command_channel = mb_channel.DEVICE_COMMAND
        self.mysql_base_url = f'{const_h.MYSQL_HOST}:{const_h.SERVICE_PORT_MYSQL}'
        self.schedule_list = []

    def start(self):
        super().start()
        self.init_mqtt_client()
        threading.Thread(target=self.get_schedule_list).start()  # update schedule list regularly
        self.start_timer()

    def stop(self):
        self.remove_mqtt_client()

    def get_schedule_list(self):
        while True:
            params = {
                'inner': True,
                'is_deleted': 0
            }
            try:
                resp = requests.get(self.mysql_base_url + const_h.MYSQL_SCHEDULE_LIST, params=params)
                resp.raise_for_status()  # Raise an error for bad responses
                self.schedule_list = resp.json().get('list', [])
                self.logger.info(f"Fetched {len(self.schedule_list)} schedules")
            except requests.RequestException as e:
                logging.error(f"Failed to fetch schedule list: {e}")
            time.sleep(30)

    def start_timer(self):
        logging.info("Starting timers for minute, hour, and day schedules")
        threading.Thread(target=self.minute_schedule).start()  # once per minute
        threading.Thread(target=self.hour_schedule).start()  # once per hour
        threading.Thread(target=self.day_schedule).start()  # once per day

    def minute_schedule(self):
        time.sleep(10)
        while True:
            time.sleep(60)
            self.logger.info("Executing minute schedule")
            self.do_schedule(60)

    def hour_schedule(self):
        time.sleep(10)
        while True:
            time.sleep(3600)
            self.logger.info("Executing hour schedule")
            self.do_schedule(3600)

    def day_schedule(self):
        time.sleep(10)
        while True:
            time.sleep(86400)
            self.logger.info("Executing day schedule")
            self.do_schedule(86400)

    def do_schedule(self, duration):
        for schedule in self.schedule_list:
            if duration != schedule['duration']:
                continue
            device = schedule['target']
            msg = json.dumps({
                'type': 'action',
                'status': schedule['opt']
            })
            try:
                self.mqtt_publish(self.command_channel + device, msg)
                logging.info(f"Published message to {self.command_channel + device}: {msg}")
            except Exception as e:
                self.logger.error(f"Failed to publish message to {self.command_channel + device}: {e}")
