import xml.etree.ElementTree as ET
import logging

def load_config(file_path='config.xml', data_key=None):
    config = {}
    tree = ET.parse(file_path)
    root = tree.getroot()

    # Base URL
    base_url = root.find('url').text

    # Port based on data_key
    if data_key == 'temperature' or data_key == 'humidity':
        port = root.find('ports/weather').text
    elif data_key == 'soil_moisture':
        port = root.find('ports/soil_moisture_sensor').text
    else:
        logging.error("Invalid data_key provided, must be 'temperature', 'humidity', or 'soil_moisture'.")
        return None

    # Data path based on data_key
    data_path = root.find(f'data_keys/{data_key}').text

    # Construct the full API URL
    config['api_url'] = f"{base_url}:{port}/{data_path}"
    config['data_key'] = data_key

    return config
