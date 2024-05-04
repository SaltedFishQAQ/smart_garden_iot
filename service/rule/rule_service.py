import json
import constants.entity
import constants.rule
import message_broker.channels as mb_channel

from common.base_service import BaseService
from service.rule.converter import convert_checker, convert_message


class RuleService(BaseService):
    def __init__(self):
        super().__init__(constants.entity.RULE_SERVICE)
        self.data_channel = mb_channel.DEVICE_DATA  # channel for get data
        self.command_channel = mb_channel.DEVICE_COMMAND  # channel for send command
        self.rule_list = demo_rule()

    def start(self):
        self.init_mqtt_client()

    def stop(self):
        self.remove_mqtt_client()

    def register_mqtt_service(self):
        # device data
        self.mqtt_listen(self.data_channel + '+', self.mqtt_data)

    def mqtt_data(self, client, userdata, msg):
        entity = msg.topic.removeprefix(self.data_channel)
        content = msg.payload.decode('utf-8')
        data_dict = json.loads(content)
        # when [entity] do ([entity.field] <compare> [value]) if true then {opt}
        for r in self.rule_list:
            if entity != r['entity']:  # rule not match
                print("rule not match")
                continue
            if ("tags" not in data_dict or
                    "device_id" not in data_dict['tags'] or
                    r['id'] != data_dict["tags"]["device_id"]):  # device not match
                print("device not match")
                continue

            compare = r['compare']  # comparison symbol
            compare_val = r['value']  # compare value
            field = r['field']  # compare field
            data_val = data_dict['fields'][field]  # real value
            opt = r['opt']  # operate

            checker = convert_checker(compare, compare_val)  # compare function
            match, ok = checker(data_val)  # compare result
            if ok is False:
                print(f"invalid rule: {r}")
            if match:
                target, msg, ok = convert_message(opt)
                if ok is False:
                    print(f"convert message false, opt: {opt}")
                self.mqtt_publish(self.command_channel+target, msg)


def demo_rule() -> list:
    # entity, field, compare, value, opt
    return [{
        'id': 'device1',
        'entity': constants.entity.TEMPERATURE,
        'field': "value",
        'compare': constants.rule.COMPARE_GREATER_THAN,
        'value': 25.0,
        'opt': constants.rule.OPT_LIGHT_OFF
    }]
