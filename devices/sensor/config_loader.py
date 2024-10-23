import xml.etree.ElementTree as ET
import logging

def load_config(file_path='config.xml', data_key=None):
    config = {}
    tree = ET.parse(file_path)
    root = tree.getroot()

    config['api_url'] = root.find('weather_api_url').text

    if data_key == 'temperature':
        config['data_key'] = root.find('data_keys/temperature').text
    elif data_key == 'humidity':
        config['data_key'] = root.find('data_keys/humidity').text
    else:
        logging.error("Invalid data_key provided, must be 'temperature' or 'humidity'.")
        return None

    return config
