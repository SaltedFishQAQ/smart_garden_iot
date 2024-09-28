import time
import json
import requests
import threading
import constants.entity
import constants.http as const_h
from common.base_service import BaseService
import message_broker.channels as mb_channel


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
            resp = requests.get(self.mysql_base_url + const_h.MYSQL_SCHEDULE_LIST)
            self.schedule_list = resp.json()['list']
            time.sleep(60)

    def start_timer(self):
        threading.Thread(target=self.minute_schedule).start()  # once per minute
        threading.Thread(target=self.hour_schedule).start()  # once per hour
        threading.Thread(target=self.day_schedule).start()  # once per day

    def minute_schedule(self):
        while True:
            time.sleep(60)
            self.do_schedule(60)

    def hour_schedule(self):
        while True:
            time.sleep(3600)
            self.do_schedule(3600)

    def day_schedule(self):
        while True:
            time.sleep(86400)
            self.do_schedule(86400)

    def do_schedule(self, duration):
        for schedule in self.schedule_list:
            if duration != schedule['duration']:
                continue
            device = schedule['target']
            msg = json.dumps({
                'status': schedule['opt']
            })
            self.mqtt_publish(self.command_channel + device, msg)
