import json
import requests
import constants.http as const_h
import message_broker.channels as mb_channel

from http import HTTPMethod
from service.rule.converter import convert_message


class Logic:
    def __init__(self, delegate):
        self.delegate = delegate
        self.command_channel = mb_channel.DEVICE_COMMAND
        self.mysql_base_url = f'{const_h.MYSQL_HOST}:{const_h.SERVICE_PORT_MYSQL}'

    def register_handler(self):
        self.delegate.http_client.add_route(const_h.USER_DEVICE_RUNNING, HTTPMethod.POST, self.running)
        self.delegate.http_client.add_route(const_h.USER_DEVICE_COMMAND, HTTPMethod.POST, self.command)
        self.delegate.http_client.add_route(const_h.USER_DEVICE_APPROVE, HTTPMethod.POST, self.approve)

    def running(self, params):
        if 'name' not in params or 'status' not in params:
            return {
                "code": 500,
                "message": "missing params: name or status"
            }

        self.delegate.mqtt_publish(self.command_channel+params['name'], json.dumps({
            'running': params['status']
        }))

        return {
            "code": 0,
            "message": "success"
        }

    def approve(self, params):
        resp = requests.post(self.mysql_base_url + const_h.MYSQL_DEVICE_APPROVE, json=params)

        return resp.json()

    def command(self, params):
        if 'name' not in params or 'opt' not in params:
            return {
                "code": 500,
                "message": "missing params: name or status"
            }

        target, msg, ok = convert_message(params['name'], params['opt'])
        if ok is False:
            return {
                "code": 500,
                "message": "invalid command"
            }
        self.delegate.mqtt_publish(self.command_channel+target, msg)

        return {
            "code": 0,
            "message": "success"
        }
