import os
import logging
import constants.http
import constants.entity
from common.base_service import BaseService
from common.config import ConfigLoader
from data import DataSource
from http import HTTPMethod

logging.basicConfig(
    filename='/tmp/api.log',
    level=logging.WARNING,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


class WeatherAdapter(BaseService):
    def __init__(self):
        super().__init__(constants.entity.OPEN_WEATHER_MAP)
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'weather_config.xml')
        config = ConfigLoader(config_path)

        self.data_source = DataSource(
            api_url=config.get("./weather/api_url"),
            api_key=config.get("./weather/api_key"),
            city=config.get("./weather/city"),
            timezone=config.get("./weather/timezone")
        )

    def start(self):
        super().start()
        self.init_http_client(host="0.0.0.0", port=5000)

    def stop(self):
        self.remove_http_client()

    def register_http_handler(self):
        self.http_client.add_route(constants.http.WEATHER_DATA_GET, HTTPMethod.GET, self.handle_data)

    def handle_data(self, params):
        try:
            weather_data = self.data_source.fetch_weather_data(params)
            if not weather_data:
                logging.error("Failed to fetch weather data from OpenWeatherMap")
                return {"error": "Failed to fetch weather data"}
            return weather_data
        except Exception as e:
            logging.error(f"An error occurred: {str(e)}")
            return {"error": "Internal server error"}
