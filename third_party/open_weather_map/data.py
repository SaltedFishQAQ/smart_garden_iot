import requests
import logging
from datetime import datetime
import pytz

logging.basicConfig(
    filename='/tmp/api.log',
    level=logging.WARNING,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


class DataSource:
    def __init__(self, api_url, api_key, city, timezone):
        self.api_url = api_url
        self.api_key = api_key
        self.city = city
        self.timezone = timezone

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
