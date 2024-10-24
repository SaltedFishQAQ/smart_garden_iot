import xml.etree.ElementTree as ET


class ConfigLoader:
    def __init__(self, config_file):
        self.config_file = config_file
        self.config_data = self.load_config()

    def load_config(self):
        tree = ET.parse(self.config_file)
        root = tree.getroot()

        config_data = {
            "api_url": root.find("./weather/api_url").text,
            "api_key": root.find("./weather/api_key").text,
            "city": root.find("./weather/city").text,
            "timezone": root.find("./weather/timezone").text,
            "mqtt_broker": root.find("./mqtt/broker").text,
            "mqtt_port": int(root.find("./mqtt/port").text),
            "command_channel": root.find("./mqtt/topic").text
        }
        return config_data
