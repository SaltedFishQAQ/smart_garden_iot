import xml.etree.ElementTree as ET


class ConfigLoader:
    def __init__(self, config_file):
        self.config_file = config_file
        self.root = None
        self.load()

    def load(self):
        tree = ET.parse(self.config_file)
        self.root = tree.getroot()

    def get(self, path):
        return self.root.find(path).text
