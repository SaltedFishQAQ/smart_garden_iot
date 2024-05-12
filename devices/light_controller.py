import json

import constants.entity
import message_broker.channels as mb_channel
from biz.base_device import BaseDevice
from actuator.light_switch import LightSwitch


class LightController(BaseDevice):
    def __init__(self, name):
        self.conf = json.load(open('./configuration.json'))
        super().__init__(name, self.conf['broker'], self.conf['port'])
        self.subscribe_topic = mb_channel.DEVICE_COMMAND + constants.entity.LIGHT
        self.actuator = LightSwitch()
        self.running = False

    def start(self):
        self.init_mqtt_client()
        self.running = True

    def register_mqtt_service(self):
        # device data
        self.mqtt_listen(self.subscribe_topic, self.on_message)

    def stop(self):
        self.remove_mqtt_client()
        self.running = False

    def on_message(self, client, userdata, msg):
        content = msg.payload.decode('utf-8')
        data_dict = json.loads(content)
        if 'device' not in data_dict:
            return
        dst = data_dict['device']
        if dst != '' and dst != self.device_name:
            return

        key = 'status'
        if key not in data_dict:
            print(f"data missing status value, data: {content}")
            return
        status = bool(data_dict[key])
        self.actuator.switch(status)
        print(f"device: {self.device_name}, current light switch {self.actuator.get_status()}")
