import requests
from datetime import datetime, timedelta
import time
import pytz

class WeatherService:
    def __init__(self, api_key, city):
        self.api_key = api_key
        self.city = city
        self.sunrise = None
        self.sunset = None
        self.rain_probability = None

    def fetch_weather_data(self):
        url = f"https://api.openweathermap.org/data/2.5/weather?q={self.city}&appid={self.api_key}"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            utc_sunrise = datetime.utcfromtimestamp(data['sys']['sunrise'])
            utc_sunset = datetime.utcfromtimestamp(data['sys']['sunset'])

            #local timezone
            local_tz = pytz.timezone('Europe/Rome')
            self.sunrise = utc_sunrise.replace(tzinfo=pytz.utc).astimezone(local_tz)
            self.sunset = utc_sunset.replace(tzinfo=pytz.utc).astimezone(local_tz)

            self.rain_probability = data.get('rain', {}).get('1h', 0)  # Rain probability (last hour)
            print(f"Sunrise: {self.sunrise}, Sunset: {self.sunset}, Rain Probability: {self.rain_probability} mm")
        else:
            print(f"Error fetching data: {response.status_code} - {response.text}")

    def check_sun_times(self):
        current_time = datetime.now(pytz.timezone('Europe/Rome'))
        print(f"Current time: {current_time}")

        if current_time >= self.sunrise and current_time < self.sunset:
            # Sunrise action
            self.trigger_action("Turn off the light")
        elif current_time >= self.sunset:
            # Sunset action
            self.trigger_action("Turn on the light")

    def trigger_action(self, action):
        print(f"Action Triggered: {action}")

    def check_rain_probability(self):
        print(f"Rain Probability Check: {self.rain_probability} mm")
        if self.rain_probability > 0:
            self.trigger_action("Close watering system")

class WeatherMicroservice:
    def __init__(self, weather_service):
        self.weather_service = weather_service

    def run(self):
        #check and action
        self.weather_service.fetch_weather_data()
        self.weather_service.check_sun_times()

        # Schedule checks: rain every 10 minutes, sunrise/sunset every 12 hours
        while True:
            current_time = datetime.utcnow()
            next_sun_check = current_time + timedelta(hours=12)
            next_rain_check = current_time + timedelta(minutes=10)

            while current_time < next_sun_check:
                # Check rain every 10 minutes
                if current_time >= next_rain_check:
                    self.weather_service.fetch_weather_data()  # Updates the weather data
                    self.weather_service.check_rain_probability()
                    next_rain_check = current_time + timedelta(minutes=10)

                time.sleep(60)
                current_time = datetime.utcnow()

            self.weather_service.fetch_weather_data()
            self.weather_service.check_sun_times()

#config
api_key = "5dc8ece6e02d649d870e2e3a67ffc128"
city = "Turin,it"
weather_service = WeatherService(api_key, city)
microservice = WeatherMicroservice(weather_service)

microservice.run()
