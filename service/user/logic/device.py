import json
import requests
import constants.http as const_h
import message_broker.channels as mb_channel
from http import HTTPMethod
from service.rule.converter import convert_message
from service.user.logic.base import Common


class Logic(Common):
    def __init__(self, delegate):
        super().__init__(delegate)
        self.command_channel = mb_channel.DEVICE_COMMAND

    def register_handler(self):
        self.delegate.http_client.add_route(const_h.USER_DEVICE_RUNNING, HTTPMethod.POST, self.running)
        self.delegate.http_client.add_route(const_h.USER_DEVICE_COMMAND, HTTPMethod.POST, self.command)
        self.delegate.http_client.add_route(const_h.USER_DEVICE_APPROVE, HTTPMethod.POST, self.approve)
        self.delegate.http_client.add_route(const_h.USER_DEVICE_STATUS, HTTPMethod.GET, self.status)

    def running(self, params):
        if self.check_device(params) is False:
            return {
                "code": 500,
                "message": "no operation permission"
            }
        if 'name' not in params or 'status' not in params:
            return {
                "code": 500,
                "message": "missing params: name or status"
            }

        if params['status'] == 1:
            opt = True
        else:
            opt = False

        self.delegate.mqtt_publish(self.command_channel+params['name'], json.dumps({
            'type': 'running',
            'status': opt
        }))

        return {
            "code": 0,
            "message": "success"
        }

    def approve(self, params):
        if self.check_device(params) is False:
            return {
                "code": 500,
                "message": "no operation permission"
            }
        self.match_area_ids(params)
        resp = requests.post(self.mysql_base_url + const_h.MYSQL_DEVICE_APPROVE, json=params)

        return resp.json()

    def command(self, params):
        if self.check_device(params) is False:
            return {
                "code": 500,
                "message": "no operation permission"
            }
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

    def status(self, params):
        if self.check_device(params) is False:
            return {
                "code": 500,
                "message": "no operation permission"
            }
        if 'name' not in params:
            return {
                "code": 500,
                "message": "missing params: name"
            }

        if params['name'] not in self.delegate.device_status:
            return {
                "code": 500,
                "message": "record not found"
            }

        return {
            "code": 0,
            "message": "success",
            "data": self.delegate.device_status[params['name']]
        }
