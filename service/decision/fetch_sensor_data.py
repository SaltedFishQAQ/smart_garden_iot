import requests
import constants.const as const
import constants.http as chttp

class SensorDataFetcher:
    def __init__(self):
        self.server_ip = chttp.SENSOR_SERVER_IP
        self.base_url = f"http://{self.server_ip}:8083/data"
        self.headers = {"Authorization": const.SENSOR_AUTH_TOKEN}

    def fetch_latest_measurement(self, measurement, area, page=1, size=10):
        """Fetch the latest measurement for a specific area."""
        params = {"measurement": measurement, "page": page, "size": size}

        try:
            response = requests.get(self.base_url, params=params, headers=self.headers, timeout=10)
            data = response.json()

            if data.get("code") != 0 or not data.get("list"):
                print(f"Error: Invalid response or no data for measurement: {measurement}")
                return None

            area_data = [entry for entry in data["list"] if entry.get("area") == area]
            if not area_data:
                print(f"No data found for area '{area}' and measurement '{measurement}'.")
                return None

            return area_data[0].get("value")

        except requests.RequestException as e:
            print(f"Network error fetching data for {measurement} in area '{area}': {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

        return None

    def get_sensor_data(self, area):
        """Fetch the latest data for humidity, temperature, and soil moisture."""
        humidity = self.fetch_latest_measurement("humidity", area)
        temperature = self.fetch_latest_measurement("temperature", area)
        soil_moisture = self.fetch_latest_measurement("soil", area)
        return humidity, temperature, soil_moisture
