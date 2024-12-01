import os
import requests
import time
import joblib
import pandas as pd
import threading
import constants.entity
import constants.const as const
import constants.http as const_h
import message_broker.channels as mb_channel
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from datetime import datetime, timedelta
from common.config import ConfigLoader
from common.base_service import BaseService
from service.decision.controller.light import LightController
from service.decision.controller.watering import WateringController


soil_types = SOIL_TYPE = {
    "sandy": {"field_capacity": 15, "wilting_point": 4, "adjustment_factor": 0.3},
    "clay": {"field_capacity": 50, "wilting_point": 15, "adjustment_factor": 1.0},  # Default base
    "loamy": {"field_capacity": 25, "wilting_point": 10, "adjustment_factor": 0.85},
    "silty": {"field_capacity": 35, "wilting_point": 12, "adjustment_factor": 0.9},
    "peaty": {"field_capacity": 40, "wilting_point": 10, "adjustment_factor": 0.88},
}


class ThresholdCalculator:
    def __init__(self, delegate):
        self.delegate = delegate
        self.window = 7
        self.file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'weather_turin.csv')
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.weather_data = None
        self._load_data()
        self._train_or_load_model()

    def _load_data(self):
        self.weather_data = pd.read_csv(self.file_path)
        self.weather_data.columns = ['time', 'cloud_cover', 'soil_moisture']
        self.weather_data['time'] = pd.to_datetime(self.weather_data['time'])
        self.weather_data['day_of_year'] = self.weather_data['time'].dt.dayofyear
        self.weather_data['smoothed_soil_moisture'] = self.weather_data['soil_moisture'].rolling(self.window).mean()
        self.weather_data.dropna(inplace=True)

    def _train_or_load_model(self):
        try:
            self.model = joblib.load("soil_moisture_model.pkl")
            self.scaler = joblib.load("scaler.pkl")
        except (FileNotFoundError, IOError):
            X = self.weather_data[['day_of_year', 'smoothed_soil_moisture']]
            y = self.weather_data['soil_moisture']
            X_scaled = self.scaler.fit_transform(X)
            X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)
            self.model.fit(X_train, y_train)
            joblib.dump(self.model, "soil_moisture_model.pkl")
            joblib.dump(self.scaler, "scaler.pkl")

    def get_daily_threshold(self, input_date, soil_type="Clay"):
        day_of_year = input_date.timetuple().tm_yday
        recent_smoothed_soil_moisture = self.weather_data['smoothed_soil_moisture'].iloc[-1]
        X_pred = pd.DataFrame([[day_of_year, recent_smoothed_soil_moisture]],
                              columns=['day_of_year', 'smoothed_soil_moisture'])
        X_pred_scaled = self.scaler.transform(X_pred)
        baseline_threshold = self.model.predict(X_pred_scaled)[0]
        soil_info = soil_types.get(soil_type.capitalize(), soil_types["clay"])  # Use clay as default
        adjustment_factor = soil_info["adjustment_factor"]
        adjusted_threshold = baseline_threshold * adjustment_factor
        return adjusted_threshold

    def calc_dynamic_threshold(self, historical_data, soil_type):
        recent_data = historical_data.tail(15)
        avg_temp_24h = recent_data['avg_temp_24h'].mean()
        avg_humidity_24h = recent_data['avg_humidity_24h'].mean()
        baseline_threshold = self.get_daily_threshold(datetime.now(), soil_type)
        adjustment_factor = const.DEFAULT_ADJUSTMENT_FACTOR
        if avg_temp_24h > const.BASELINE_TEMP_FOR_ADJUSTMENT:
            temperature_factor = 1 - (
                    (avg_temp_24h - const.BASELINE_TEMP_FOR_ADJUSTMENT) * const.TEMP_ADJUSTMENT_FACTOR
            )
            adjustment_factor *= temperature_factor
        if avg_humidity_24h < const.BASELINE_HUMIDITY_FOR_ADJUSTMENT:
            humidity_factor = 1 - (
                (const.BASELINE_HUMIDITY_FOR_ADJUSTMENT - avg_humidity_24h) * const.HUMIDITY_ADJUSTMENT_FACTOR
            )
            adjustment_factor *= humidity_factor
        return baseline_threshold * adjustment_factor, soil_types[soil_type]['adjustment_factor']


class DecisionService(BaseService):
    def __init__(self):
        super().__init__(constants.entity.DECISION_SERVICE)
        self.control_groups = []
        self.command_channel = mb_channel.DEVICE_COMMAND
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'configuration.xml')
        self.config = ConfigLoader(config_path)
        self.weather_api_url = self.config.get("./weather/api_url")
        self.mqtt_broker = self.config.get("./mqtt/broker")
        self.mqtt_port = self.config.get("./mqtt/port")
        self.mqtt_topic = self.config.get("./mqtt/topic")
        self.timezone = self.config.get("./weather/timezone")
        self.threshold_calculator = ThresholdCalculator(self)

    def start(self):
        super().start()
        self.init_mqtt_client()
        self.register_controller()
        threading.Thread(target=self.run).start()

    def stop(self):
        self.remove_mqtt_client()

    def fetch_weather_data(self):
        """
        Fetch weather data from the weather API and update sunrise and sunset times.
        """
        try:
            response = requests.get(self.weather_api_url + const_h.WEATHER_DATA_GET, {})
            if response.status_code == 200:
                data = response.json()
                for group in self.control_groups:
                    group.handle_data(data)
            else:
                self.logger.error(f"Failed to fetch weather data. Status code: {response.status_code}")
        except Exception as e:
            self.logger.error(f"Error fetching weather data: {e}")

    def run(self):
        """
        Main loop that fetches weather data once a day and checks for light control every 10 minutes.
        """
        self.logger.info(f'decision service start..., there are {len(self.control_groups)} control groups')
        time.sleep(4*60)
        while True:
            self.logger.info('-------- check data start --------')
            self.fetch_weather_data()
            for group in self.control_groups:
                group.handle_check()
            self.logger.info('-------- check data end --------')
            time.sleep(10*60)

    def register_controller(self):
        self.control_groups = [
            LightController(self),
            WateringController(self)
        ]
