import json
import time

import requests
import constants.http as const_h
import message_broker.channels as mb_channel
import threading
from common.mqtt import MQTTClient


class BaseDevice:
    def __init__(self, name, broker="10.9.0.10", port=1883):
        # meta
        self.device_name = name
        self.working = False
        self.broker = broker
        self.port = port
        # communication
        self.mqtt_client = None
        self.register_url = f'{const_h.MYSQL_HOST}:{const_h.SERVICE_PORT_MYSQL}{const_h.MYSQL_DEVICE_REGISTER}'
        self.data_topic = mb_channel.DEVICE_DATA + name
        self.command_topic = mb_channel.DEVICE_COMMAND + name
        self.operation_topic = mb_channel.DEVICE_OPERATION
        # func
        self.sensor = None
        self.actuator = None

    def start(self):
        self.init_mqtt_client()
        threading.Thread(target=self.notify_status).start()
        self._set_working(True)

    def stop(self):
        self.remove_mqtt_client()
        self._set_working(False)

    def init_mqtt_client(self):
        if self.mqtt_client is not None:
            return

        self.mqtt_client = MQTTClient(self.device_name, self.broker, self.port)
        self.mqtt_client.start()
        self.mqtt_listen(self.command_topic, self._handle_command)

    def remove_mqtt_client(self):
        if self.mqtt_client is None:
            return

        self.mqtt_client.stop()
        self.mqtt_client = None

    def mqtt_listen(self, topic, callback):
        if self.mqtt_client is None:
            return False, "mqtt_client is none"
        self.mqtt_client.subscribe(topic, callback)

        return True, ""

    def mqtt_publish(self, topic, message):
        if self.mqtt_client is None:
            return False, "mqtt_client is none"

        self.mqtt_client.publish(topic, message)
        return True, ""

    def record_data(self, data):
        mqtt_data = {
            'tags': {
                'device': self.device_name,
            },
            'fields': data,
        }
        self.mqtt_publish(self.data_topic, json.dumps(mqtt_data))

    def record_operation(self, message):
        mqtt_data = {
            'tags': {
                'device': self.device_name,
            },
            'fields': message,
        }
        self.mqtt_publish(self.operation_topic, json.dumps(mqtt_data))

    def _handle_command(self, client, userdata, msg):
        content = msg.payload.decode('utf-8')
        print(f'_handle_command: {content}')
        data_dict = json.loads(content)
        print(f"device: {self.device_name}, receive command: {data_dict}")

        if 'type' not in data_dict:
            print(f"data missing type value, data: {content}")
            return
        types = data_dict['type']

        if 'status' not in data_dict:
            print(f"data missing status value, data: {content}")
            return
        status = bool(data_dict['status'])

        if types == 'running':
            self._set_working(status)
            print(f"device: {self.device_name}, set running status: {status}")
        else:
            if self.working:
                self.handle_opt(types, status)

    def _set_working(self, status):
        if self.working == status:
            return
        self.working = status
        self.handle_working(status)

        data = {
            'name': self.device_name,
            'status': 0
        }
        if self.working:
            data['status'] = 1

        _ = requests.post(self.register_url, json=data)

    def handle_working(self, status):
        pass

    def handle_opt(self, opt, status):
        pass

    def notify_status(self):
        while True:
            data = self.status()
            self.mqtt_client.publish(mb_channel.DEVICE_STATUS + self.device_name, json.dumps(data))
            time.sleep(30)

    def status(self):
        return {
            'device': self.working
        }
