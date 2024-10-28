import cherrypy
import logging
from config_loader import ConfigLoader
from weather_service import WeatherService

logging.basicConfig(
    filename='/tmp/api.log',
    level=logging.WARNING,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

class WeatherAPI:
    def __init__(self):
        config_loader = ConfigLoader('weather_config.xml')
        config = config_loader.config_data

        # Initialize weather service
        self.weather_service = WeatherService(
            api_url=config['api_url'],
            api_key=config['api_key'],
            city=config['city'],
            timezone=config['timezone']
        )

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def weather(self, data=None):
        """
        Fetch the weather data and optionally return only specific fields based on the query parameter `data`.
        """
        try:
            weather_data = self.weather_service.fetch_weather_data()
            if not weather_data:
                cherrypy.response.status = 500
                logging.error("Failed to fetch weather data from OpenWeatherMap")
                return {"error": "Failed to fetch weather data"}

            if data:
                if data in weather_data:
                    return {data: weather_data[data]}
                else:
                    return {"error": f"'{data}' is not a valid field"}

            return weather_data
        except Exception as e:
            logging.error(f"An error occurred: {str(e)}")
            cherrypy.response.status = 500
            return {"error": "Internal server error"}

if __name__ == '__main__':
    # CherryPy configuration
    cherrypy.config.update({
        'server.socket_host': '0.0.0.0',
        'server.socket_port': 5000,
    })
    # Start the API
    weather_api = WeatherAPI()
    cherrypy.quickstart(weather_api, '/')

