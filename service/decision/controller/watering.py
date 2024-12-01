import time
import requests
import pandas as pd
import constants.const as const
import constants.http as const_h
import message_broker.channels as mb_channel
from datetime import datetime
from common.log import Logger
from common.time import time_add
from constants.const import MIN_CLOUDINESS_FOR_WATERING, MIN_RAIN_PROBABILITY
from service.decision.controller.base import BaseController

SOIL_ABSORPTION_FACTOR = {
    "sandy": "0.85",
    "clay": "0.3",
    "loamy": "0.7",
    "silty": "0.6",
    "peaty": "0.8"
}


class DataFetcher:
    def __init__(self, delegate):
        self.delegate = delegate
        self.mysql_base_url = f'{const_h.MYSQL_HOST}:{const_h.SERVICE_PORT_MYSQL}'

    def fetch(self):
        self.get_area_list()
        self.get_sensor_data()
        self.get_history_weather()
        self.get_irrigator_list()

    def get_irrigator_list(self):
        params = {'inner': True}
        resp = requests.get(self.mysql_base_url + const_h.MYSQL_DEVICE_LIST, params)
        device_list = resp.json()['list']
        actuator_map = {}
        for device in device_list:
            if device['actuator'] != 'irrigator':
                continue
            area_id = device['area_id']
            irrigator_list = []
            if area_id in actuator_map:
                irrigator_list = actuator_map[area_id]
            irrigator_list.append(device)
            actuator_map[area_id] = irrigator_list
        self.delegate.actuator_map = actuator_map

    def get_area_list(self):
        resp = requests.get(self.mysql_base_url + const_h.MYSQL_AREA_LIST)
        self.delegate.area_list = resp.json()['list']

    def get_sensor_data(self):
        params = {'inner': True}
        need_measurements = ['humidity', 'temperature', 'soil']
        sensor_data = {}
        for measurement in need_measurements:
            for area in self.delegate.area_list:
                params['measurement'] = measurement
                params['area_list'] = list([area['name']])
                resp = requests.get(self.delegate.sensor_api_url, params)
                data_list = resp.json()['list']
                self.delegate.logger.info(f'{params}, {(area["id"], measurement)} fetch data: {data_list}')
                if data_list is None or len(data_list) == 0:
                    sensor_data[(area['id'], measurement)] = None
                    continue
                sensor_data[(area['id'], measurement)] = data_list[0]
        self.delegate.sensor_data = sensor_data

    def get_history_weather(self):
        resp = requests.get(self.delegate.weather_api_url + const_h.HISTORICAL_WEATHER_GET)
        json_data = resp.json()
        weather_df = pd.DataFrame(json_data)
        if 'time' not in weather_df or 'temperature_2m' not in weather_df or 'relative_humidity_2m' not in weather_df:
            self.delegate.logger.error("Missing required columns in the data.")
            return pd.DataFrame()
        weather_df['time'] = pd.to_datetime(weather_df['time'])
        weather_df['cumulative_rain'] = weather_df['precipitation'].cumsum()
        min_periods = min(24, len(weather_df))  # Use available data if < 24 rows
        weather_df['avg_temp_24h'] = weather_df['temperature_2m'].rolling(window=24, min_periods=min_periods).mean()
        weather_df['avg_humidity_24h'] = weather_df['relative_humidity_2m'].rolling(window=24,
                                                                                    min_periods=min_periods).mean()
        self.delegate.historical_data = weather_df


class SoilMoisturePredictor:
    def __init__(self, delegate):
        self.delegate = delegate

    def predict_after_rain(self, area):
        current_soil_moisture = float(self.delegate.sensor_data[(area['id'], 'soil')]['value'])
        rain_amount = self.delegate.weather_data['rain_probability']
        soil_absorption_factor = SOIL_ABSORPTION_FACTOR.get(area['soil_type'], float(0.5))
        moisture_increase = rain_amount * soil_absorption_factor
        predicted_soil_moisture = current_soil_moisture + moisture_increase

        return min(predicted_soil_moisture, 1.0)


class DecisionMaker:
    def __init__(self, delegate, area):
        self.delegate = delegate
        self.logger = Logger(prefix=f'watering decision/{area["name"]}')
        self.area = area
        self.soil_moisture = delegate.sensor_data[(area['id'], 'soil')]

    def calc_duration(self):
        rain_mm = float(self.delegate.weather_data.get("rain_probability", 0))
        threshold, adjustment_factor = self.delegate.threshold.calc_dynamic_threshold(
            self.delegate.historical_data, self.area['soil_type'])
        predictor = SoilMoisturePredictor(self.delegate)
        predicted_soil_moisture = predictor.predict_after_rain(self.area)
        if predicted_soil_moisture >= threshold:
            return 0
        moisture_deficit = (threshold * 100) - (self.soil_moisture * 100)
        required_water = (moisture_deficit * const.DEPTH * const.DENSITY * const.CUBIC_AREA) / 100
        water_adjustment = required_water * adjustment_factor
        rain_adjustment = rain_mm * const.CUBIC_AREA * adjustment_factor
        duration = (water_adjustment - rain_adjustment) / const.VALVE_FLOW_RATE
        return max(0, duration)

    def make_decision(self):
        cloudiness = self.delegate.weather_data["cloudiness"]
        sunrise = datetime.fromisoformat(self.delegate.weather_data["sunrise"])
        sunset = datetime.fromisoformat(self.delegate.weather_data["sunset"])
        now = datetime.now(sunrise.tzinfo)

        if time_add(sunrise, 60 * 60) <= now <= time_add(sunset, -60 * 60) and cloudiness < MIN_CLOUDINESS_FOR_WATERING:
            # skip watering
            return 0

        return self.calc_duration()


class WateringController(BaseController):
    def __init__(self, delegate):
        self.delegate = delegate
        self.logger = Logger(prefix=f'watering controller:')
        self.weather_data = None
        self.sensor_data = None
        self.actuator_map = {}
        self.historical_data = None
        self.area_list = []
        self.threshold = delegate.threshold_calculator
        self.weather_api_url = delegate.weather_api_url
        # self.sensor_api_url = delegate.config.get("./sensor/api_url")
        self.sensor_api_url = f'{const_h.INFLUX_HOST}:{const_h.SERVICE_PORT_INFLUX}{const_h.INFLUX_DATA_GET}'
        self.data_source = DataFetcher(self)
        self.command_channel = mb_channel.DEVICE_COMMAND

    def handle_data(self, data):
        # current data
        self.weather_data = data
        self.data_source.fetch()

    def handle_command(self, area, minutes):
        device_list = self.actuator_map[area['id']]
        duration = minutes * 60
        # irrigator on
        params = {
            'type': 'action',
            'status': True
        }
        for device in device_list:
            self.delegate.mqtt_publish(self.command_channel + device['name'], params)
        time.sleep(duration)
        # irrigator off
        params['status'] = False
        for device in device_list:
            self.delegate.mqtt_publish(self.command_channel + device['name'], params)

    def handle_check(self):
        for area in self.area_list:
            if self.need_check(area) is False:
                continue
            maker = DecisionMaker(self, area)
            decision = maker.make_decision()
            if decision <= 0:
                continue
            self.logger.info(f'Trigger decision - {area["name"]} watering for {decision} minutes')
            self.handle_command(area, decision)

    def need_check(self, area):
        area_id = area['id']
        if area_id not in self.actuator_map:
            return False
        humidity = self.sensor_data[(area_id, 'humidity')]
        temperature = self.sensor_data[(area_id, 'temperature')]
        soil_moisture = self.sensor_data[(area_id, 'soil')]
        if humidity is None or temperature is None or soil_moisture is None:
            self.logger.warning(f'{area["name"]} missing data')
            return False

        rain_prob = self.weather_data['rain_probability']
        if rain_prob <= MIN_RAIN_PROBABILITY:
            return True

        return False
