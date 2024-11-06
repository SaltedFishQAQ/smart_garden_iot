import os
import xml.etree.ElementTree as ET


class ConfigLoader:
    def __init__(self, config_file):
        self.config_file = config_file
        self.root = None
        self.load()

    def load(self):
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), self.config_file)
        tree = ET.parse(config_path)
        self.root = tree.getroot()

    def get(self, path):
        return self.root.find(path).text
