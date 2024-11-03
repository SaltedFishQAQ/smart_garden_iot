import requests
from datetime import datetime, timedelta


class SensorDataFetcher:
    def __init__(self, influx_url, default_hours=1):

        self.influx_url = influx_url
        self.default_hours = default_hours

    def fetch_data(self, measurement, hours=None):

        if hours is None:
            hours = self.default_hours

        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours)

        params = {
            "measurement": measurement,
            "start_at": start_time.strftime("%Y-%m-%d %H:%M:%S"),
            "stop_at": end_time.strftime("%Y-%m-%d %H:%M:%S"),
            "page": 1,
            "size": 1
        }

        response = requests.get(self.influx_url, params=params)

        if response.status_code == 200:
            data = response.json().get('list', [])
            return data
        else:
            print(f"Failed to fetch {measurement} data:", response.status_code, response.text)
            return None




# Example usage

# Initialize the fetcher with the InfluxDB URL
fetcher = SensorDataFetcher("http://43.131.48.203:8084/influx/data")

# Fetch data for each type
humidity_data = fetcher.fetch_data("humidity")
temperature_data = fetcher.fetch_data("temperature")
soil_moisture_data = fetcher.fetch_data("soil_moisture")

print(humidity_data, temperature_data, soil_moisture_data)
