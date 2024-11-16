import xml.etree.ElementTree as ET


class ConfigLoader:
    def __init__(self, config_file):
        self.config_file = config_file
        self.root = None
        self.load()

    def load(self):
        tree = ET.parse(self.config_file)
        self.root = tree.getroot()

    def json(self, element=None):
        if element is None:
            element = self.root
        result = {}
        for child in element:
            if len(list(child)) > 0:
                child_dict = self.json(child)
            else:
                child_dict = child.text.strip() if child.text else ""
            if child.tag in result:
                if not isinstance(result[child.tag], list):
                    result[child.tag] = [result[child.tag]]
                result[child.tag].append(child_dict)
            else:
                result[child.tag] = child_dict
        return result

    def get(self, path):
        return self.root.find(path).text
