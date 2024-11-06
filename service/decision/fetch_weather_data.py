import requests
import pandas as pd
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(filename='weather_fetcher.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class WeatherFetcher:
    def __init__(self, current_api_url, historical_api_url):
        self.current_api_url = current_api_url
        self.historical_api_url = historical_api_url

    def fetch_current_weather_data(self):
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
        try:
            logging.info("Fetching historical weather data from custom API.")
            response = requests.get(self.historical_api_url)

            # Check for a valid response
            if response.status_code != 200 or not response.content:
                logging.error("Invalid or empty response from historical weather API.")
                return pd.DataFrame()

            # Parse JSON data
            json_data = response.json()
            weather_df = pd.DataFrame(json_data)

            # Check for required columns
            if 'time' not in weather_df or 'temperature_2m' not in weather_df or 'relative_humidity_2m' not in weather_df:
                logging.error("Missing required columns in the data.")
                return pd.DataFrame()

            # Convert time to datetime and process rolling calculations
            weather_df['time'] = pd.to_datetime(weather_df['time'])
            weather_df['cumulative_rain'] = weather_df['precipitation'].cumsum()

            min_periods = min(24, len(weather_df))  # Use available data if < 24 rows
            weather_df['avg_temp_24h'] = weather_df['temperature_2m'].rolling(window=24, min_periods=min_periods).mean()
            weather_df['avg_humidity_24h'] = weather_df['relative_humidity_2m'].rolling(window=24, min_periods=min_periods).mean()

            logging.info("Processed historical weather data with rolling averages.")
            return weather_df

        except requests.RequestException as e:
            logging.error(f"Error fetching historical weather data: {e}")
            return pd.DataFrame()