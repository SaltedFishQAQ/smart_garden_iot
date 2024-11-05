# fetch_weather_data.py

import requests
import pandas as pd
import logging
from datetime import datetime, timedelta
import requests_cache
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import pytz
from config_loader import load_sensor_config

# Load the configuration
config = load_sensor_config('sensor_config.xml')

# Setup logging
logging.basicConfig(filename='weather_fetcher.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Setup retry strategy and caching for requests
retry_strategy = Retry(
    total=5,
    backoff_factor=0.2,
    allowed_methods=["GET", "POST"],
    status_forcelist=[429, 500, 502, 503, 504]
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session = requests_cache.CachedSession('.cache', expire_after=3600)
session.mount("https://", adapter)
session.mount("http://", adapter)


class WeatherFetcher:
    def __init__(self, current_api_url, historical_api_url):
        """
        Initializes the WeatherFetcher with API URLs for current and historical data.

        Parameters:
            current_api_url (str): API endpoint for fetching current weather data.
            historical_api_url (str): API endpoint for fetching historical weather data.
        """
        self.current_api_url = current_api_url
        self.historical_api_url = historical_api_url
        self.timezone = config['timezone']
        self.latitude = config['latitude']
        self.longitude = config['longitude']
        self.rome_tz = pytz.timezone(self.timezone)

    def fetch_current_weather_data(self):
        """Fetches current weather data from the specified API."""
        try:
            response = requests.get(self.current_api_url)
            response.raise_for_status()
            data = response.json()
            filtered_data = {
                "sunrise": data.get("sunrise"),
                "sunset": data.get("sunset"),
                "cloudiness": data.get("cloudiness"),
                "rain_probability": data.get("rain_probability")
            }
            logging.info("Fetched current weather data successfully.")
            return filtered_data
        except requests.RequestException as e:
            logging.error(f"Error fetching current weather data: {e}")
            return None

    def fetch_historical_weather_data(self):
        """Fetches historical weather data for the past 15 days from the specified API."""
        try:
            logging.info("Fetching historical weather data from Open-Meteo API.")
            end_time = datetime.now(self.rome_tz)
            start_time = end_time - timedelta(days=15)

            params = {
                "latitude": self.latitude,
                "longitude": self.longitude,
                "start_date": start_time.strftime('%Y-%m-%d'),
                "end_date": end_time.strftime('%Y-%m-%d'),
                "hourly": ["temperature_2m", "relative_humidity_2m", "precipitation"],
                "timezone": self.timezone
            }

            response = session.get(self.historical_api_url, params=params)
            response.raise_for_status()
            json_data = response.json()

            # Parse hourly weather data into a DataFrame
            hourly_data = json_data.get("hourly", {})
            weather_df = pd.DataFrame(hourly_data)

            # Ensure the DataFrame has data before processing
            if weather_df.empty:
                logging.warning("Fetched historical weather data is empty.")
                return pd.DataFrame()  # Return empty DataFrame if no data

            # Calculate derived columns
            weather_df['cumulative_rain'] = weather_df['precipitation'].cumsum()
            weather_df['avg_temp_24h'] = weather_df['temperature_2m'].rolling(window=24).mean()
            weather_df['avg_humidity_24h'] = weather_df['relative_humidity_2m'].rolling(window=24).mean()

            logging.info("Fetched and processed historical weather data successfully.")
            return weather_df

        except Exception as e:
            logging.error(f"Error fetching historical weather data: {e}")
            raise


# Testing
if __name__ == "__main__":
    current_weather_api_url = "http://ec2-3-79-189-115.eu-central-1.compute.amazonaws.com:5000/weather"
    historical_weather_api_url = config['api_url']

    weather_fetcher = WeatherFetcher(current_weather_api_url, historical_weather_api_url)

    current_weather = weather_fetcher.fetch_current_weather_data()
    if current_weather:
        print("Current Weather Data:")
        print(f"  Sunrise: {current_weather['sunrise']}")
        print(f"  Sunset: {current_weather['sunset']}")
        print(f"  Cloudiness: {current_weather['cloudiness']}%")
        print(f"  Rain Probability: {current_weather['rain_probability']} mm")

    historical_weather = weather_fetcher.fetch_historical_weather_data()
    if not historical_weather.empty:
        print("\nHistorical Weather Data (Past 15 Days):")
        print(historical_weather.tail())
