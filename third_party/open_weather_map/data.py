import requests
import logging
import pytz
from common.time import time_add, time_to_str
from datetime import datetime

logging.basicConfig(
    filename='/tmp/api.log',
    level=logging.WARNING,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


class DataSource:
    def __init__(self, api_url, api_key, city, timezone, historical_api_url, lat, lon):
        self.api_url = api_url
        self.api_key = api_key
        self.city = city
        self.timezone = timezone
        self.historical_api_url = historical_api_url
        self.latitude = lat
        self.longitude = lon
        self.history_date = '2024-11-01'
        self.history_data = None

    def fetch_weather_data(self, data_type):
        data = self._get_data()
        if data_type == '':
            return data
        return {data_type: data[data_type]}

    def _get_data(self):
        try:
            url = f"{self.api_url}?q={self.city}&appid={self.api_key}&units=metric"
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                data = response.json()

                sys_data = data.get('sys', {})
                sunrise_timestamp = sys_data.get('sunrise')
                sunset_timestamp = sys_data.get('sunset')

                sunrise = datetime.utcfromtimestamp(sunrise_timestamp).replace(tzinfo=pytz.utc).astimezone(pytz.timezone(self.timezone))
                sunset = datetime.utcfromtimestamp(sunset_timestamp).replace(tzinfo=pytz.utc).astimezone(pytz.timezone(self.timezone))

                weather_info = {
                    "temperature": data['main']['temp'],
                    "humidity": data['main']['humidity'],
                    "rain_probability": data.get('rain', {}).get('1h', 0),
                    "wind_speed": data['wind']['speed'],
                    "sunrise": sunrise.isoformat(),
                    "sunset": sunset.isoformat(),
                    "cloudiness": data.get('clouds', {}).get('all', 0),  # Cloud cover percentage
                    "description": data['weather'][0]['description'],    # Weather condition description
                    "pressure": data['main']['pressure'],                # Atmospheric pressure
                    "visibility": data.get('visibility', 10000)          # Visibility in meters
                }

                return weather_info
            else:
                logging.error(f"Failed to fetch weather data. Status code: {response.status_code}")
                return None

        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching weather data: {str(e)}")
            return None

    def fetch_historical_weather_data(self):
        if not (self.historical_api_url and self.latitude and self.longitude):
            logging.error("Historical weather data configuration missing.")
            return None

        end_time = datetime.now(pytz.timezone(self.timezone))
        start_time = time_add(end_time, seconds=15*24*60*60)

        last_date = time_to_str(end_time, '%Y-%m-%d')
        if last_date == self.history_date and self.history_data is not None:
            return self.history_data
        self.history_date = last_date

        params = {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "start_date": start_time.strftime('%Y-%m-%d'),
            "end_date": end_time.strftime('%Y-%m-%d'),
            "hourly": ["temperature_2m", "relative_humidity_2m", "precipitation"],
            "timezone": self.timezone
        }

        response = requests.get(self.historical_api_url, params=params, timeout=10)
        response.raise_for_status()
        json_data = response.json()

        hourly_data = json_data.get("hourly", {})
        if not hourly_data:
            logging.warning("No hourly data found in historical weather response.")
            return None

        self.history_data = hourly_data

        return hourly_data
