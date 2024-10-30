import xml.etree.ElementTree as ET


class ConfigLoader:
    def __init__(self, config_file):
        self.config_file = config_file
        self.config_data = {
            "api_url": "http://3.79.189.115:5000/weather",
            "timezone": "Europe/Rome",
            "mqtt_broker": "mqtt.eclipseprojects.io",
            "mqtt_port": 1883,
            "mqtt_topic": "iot/lwx123321/test/",
        }
        self.load()

    def load(self):
        tree = ET.parse(self.config_file)
        root = tree.getroot()

        self.config_data = {
            "api_url": root.find("./weather/api_url").text,
            "timezone": root.find("./weather/timezone").text,
            "mqtt_broker": root.find("./mqtt/broker").text,
            "mqtt_port": int(root.find("./mqtt/port").text),
            "mqtt_topic": root.find("./mqtt/topic").text,
        }