import requests

class WeatherFetcher:
    def __init__(self, api_url):
        self.api_url = api_url

    def fetch_weather_data(self):
        try:
            response = requests.get(self.api_url)
            response.raise_for_status()
            data = response.json()
            filtered_data = {
                "sunrise": data.get("sunrise"),
                "sunset": data.get("sunset"),
                "cloudiness": data.get("cloudiness"),
                "rain_probability": data.get("rain_probability")
            }
            return filtered_data
        except requests.RequestException as e:
            print(f"Error fetching weather data: {e}")
            return None

# Testing
if __name__ == "__main__":
    api_url = "http://ec2-3-79-189-115.eu-central-1.compute.amazonaws.com:5000/weather"
    weather_fetcher = WeatherFetcher(api_url)

    weather_data = weather_fetcher.fetch_weather_data()
    if weather_data:
        print("Weather Data")
        print(f"  Sunrise: {weather_data['sunrise']}")
        print(f"  Sunset: {weather_data['sunset']}")
        print(f"  Cloudiness: {weather_data['cloudiness']}%")
        print(f"  Rain Probability: {weather_data['rain_probability']} mm")
