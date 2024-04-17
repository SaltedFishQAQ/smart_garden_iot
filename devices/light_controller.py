import json

from biz.base_device import BaseDevice
from actuator.light_switch import LightSwitch


class LightController(BaseDevice):
    def __init__(self, name):
        super().__init__(name, "mqtt.eclipseprojects.io", 1883)
        self.subscribe_topic = 'iot/lwx123321/test/light'
        self.actuator = LightSwitch()
        self.init_mqtt_client()
        self.mqtt_listen(self.subscribe_topic, self.on_message)
        self.running = False

    def start(self):
        self.running = True

    def stop(self):
        self.running = False

    def on_message(self, client, userdata, msg):
        content = msg.payload.decode('utf-8')
        data_dict = json.loads(content)
        key = 'status'
        if key not in data_dict:
            print(f"data missing status value, data: {content}")
            return
        status = bool(data_dict[key])
        self.actuator.switch(status)
        print(f"device_id: {int(data_dict['device_id'])}, current light switch {self.actuator.get_status()}")
