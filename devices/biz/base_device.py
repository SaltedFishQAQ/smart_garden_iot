import json
import time
import requests
import constants.http as const_h
import message_broker.channels as mb_channel
import threading
from common.log import Logger
from common.mqtt import MQTTClient


class BaseDevice:
    def __init__(self, area_name, name, broker="43.131.48.203", port=1883):
        # meta
        self.area_name = area_name
        self.device_name = name
        self.working = False
        self.broker = broker
        self.port = port
        # communication
        self.mqtt_client = None
        self.register_url = f'{const_h.MYSQL_HOST}:{const_h.SERVICE_PORT_MYSQL}{const_h.MYSQL_DEVICE_REGISTER}'
        self.data_topic = mb_channel.DEVICE_DATA
        self.command_topic = mb_channel.DEVICE_COMMAND + name
        self.operation_topic = mb_channel.DEVICE_OPERATION
        # func
        self.sensor = None
        self.actuator = None
        self.logger = Logger(prefix=f'{area_name}/{name}:')

    def start(self):
        self.init_mqtt_client()
        threading.Thread(target=self.notify_status).start()
        self._set_working(True)
        self.logger.info("device start")

    def stop(self):
        self.remove_mqtt_client()
        self._set_working(False)
        self.logger.info("device stop")

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

    def record_data(self, measurement, data):
        mqtt_data = {
            'tags': {
                'area': self.area_name,
                'device': self.device_name,
            },
            'fields': data,
        }
        self.mqtt_publish(self.data_topic + measurement, json.dumps(mqtt_data))

    def record_operation(self, message):
        mqtt_data = {
            'tags': {
                'area': self.area_name,
                'device': self.device_name,
            },
            'fields': message,
        }
        self.mqtt_publish(self.operation_topic, json.dumps(mqtt_data))

    def _handle_command(self, client, userdata, msg):
        content = msg.payload.decode('utf-8')
        try:
            data_dict = json.loads(content)
        except Exception as e:
            self.logger.error(f'_handle_command json convert error: {e}, content:{content}')
            return

        if 'type' not in data_dict or 'status' not in data_dict:
            self.logger.warning(f"_handle_command data missing fields, data: {content}")
            return
        types = data_dict['type']
        status = bool(data_dict['status'])

        if types == 'running':
            self._set_working(status)
            self.logger.info(f"set running status: {status}")
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
            'area': self.area_name,
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
