
# watering_duration.py

import json
from datetime import datetime
from config_loader import load_sensor_config
from fetch_weather_data import WeatherFetcher
from fetch_sensor_data import TemperatureSensor, HumiditySensor, SoilMoistureSensor
from calculate_thresholds import ThresholdCalculator  # Import ThresholdCalculator

# Load configuration
config = load_sensor_config('sensor_config.xml')

# Define soil types with respective characteristics
soil_types = {
    "Sandy": {"field_capacity": 10, "wilting_point": 4, "et_level": "High"},
    "Clay": {"field_capacity": 50, "wilting_point": 15, "et_level": "Low"},
    "Loamy": {"field_capacity": 25, "wilting_point": 10, "et_level": "Moderate"},
    "Silty": {"field_capacity": 35, "wilting_point": 12, "et_level": "Moderate"},
    "Peaty": {"field_capacity": 40, "wilting_point": 10, "et_level": "Moderate"},
}

class WateringDurationCalculator:
    def __init__(self, weather_fetcher, temperature_sensor, humidity_sensor, soil_moisture_sensor, threshold_calculator,
                 soil_type="Clay", base_duration=15, temp_threshold=25, humidity_threshold=40):
        """
        Initializes the WateringDurationCalculator with thresholds and sensors for real-time data.

        Parameters:
            weather_fetcher (WeatherFetcher): Instance of WeatherFetcher to get current weather data.
            temperature_sensor (TemperatureSensor): Instance of TemperatureSensor for temperature data.
            humidity_sensor (HumiditySensor): Instance of HumiditySensor for humidity data.
            soil_moisture_sensor (SoilMoistureSensor): Instance of SoilMoistureSensor for soil moisture data.
            threshold_calculator (ThresholdCalculator): Instance of ThresholdCalculator for dynamic thresholds.
            soil_type (str): Type of soil being used (e.g., "Sandy", "Clay", etc.).
            base_duration (int): Base watering duration in minutes.
            temp_threshold (int): Temperature threshold for adjusting watering.
            humidity_threshold (int): Humidity threshold for adjusting watering.
        """
        self.weather_fetcher = weather_fetcher
        self.temperature_sensor = temperature_sensor
        self.humidity_sensor = humidity_sensor
        self.soil_moisture_sensor = soil_moisture_sensor
        self.threshold_calculator = threshold_calculator
        self.base_duration = base_duration
        self.temp_threshold = temp_threshold
        self.humidity_threshold = humidity_threshold

        # Set soil characteristics based on soil type
        self.soil_type = soil_type
        self.field_capacity = soil_types[soil_type]["field_capacity"]
        self.wilting_point = soil_types[soil_type]["wilting_point"]
        self.et_level = soil_types[soil_type]["et_level"]

    def calculate_duration(self):
        """
        Calculate the watering duration based on sensor and current weather data.

        Returns:
            int: Calculated watering duration in minutes.
        """
        # Fetch dynamic soil moisture threshold for today
        today_str = datetime.now().strftime('%Y-%m-%d')
        thresholds = self.threshold_calculator.get_daily_threshold(today_str)
        soil_moisture_threshold = thresholds['soil_moisture_threshold']

        # Fetch sensor data and parse JSON strings
        soil_moisture_data = json.loads(self.soil_moisture_sensor.monitor())
        temperature_data = json.loads(self.temperature_sensor.monitor())
        humidity_data = json.loads(self.humidity_sensor.monitor())

        # Fetch current weather data
        current_weather = self.weather_fetcher.fetch_current_weather_data()

        # Parse values from the data
        soil_moisture = float(soil_moisture_data.get('soil_moisture', 0))
        temperature = float(temperature_data.get('temperature', 0))
        humidity = float(humidity_data.get('humidity', 0))
        rain_mm = float(current_weather.get("rain_probability", 0))

        # Soil moisture adjustment: adjust based on field capacity and wilting point
        if soil_moisture < self.field_capacity:
            soil_adjustment_factor = (self.field_capacity - soil_moisture) / (self.field_capacity - self.wilting_point)
            moisture_adjustment = max(0, soil_adjustment_factor * 20)  # Scaling factor for soil type
        else:
            moisture_adjustment = 0

        # Temperature, humidity, and rain adjustments
        temp_adjustment = max(0, (temperature - self.temp_threshold) * 2)
        humidity_adjustment = max(0, (self.humidity_threshold - humidity) * 0.5)
        rain_adjustment = rain_mm * 5

        # Calculate total watering duration
        duration = self.base_duration + moisture_adjustment + temp_adjustment + humidity_adjustment - rain_adjustment
        return max(0, duration)  # Ensure non-negative duration

# Example usage
if __name__ == "__main__":
    # Initialize WeatherFetcher and sensors
    current_weather_api_url = "http://ec2-3-79-189-115.eu-central-1.compute.amazonaws.com:5000/weather"
    historical_weather_api_url = config['api_url']
    weather_fetcher = WeatherFetcher(current_weather_api_url, historical_weather_api_url)

    file_path = 'weather_turin.csv'
    threshold_calculator = ThresholdCalculator(file_path, n_estimators=100, window=7)

    soiltypes = 'Clay'

    temperature_sensor = TemperatureSensor()
    humidity_sensor = HumiditySensor()
    soil_moisture_sensor = SoilMoistureSensor(soil_type=soiltypes)

    watering_calculator = WateringDurationCalculator(
        weather_fetcher=weather_fetcher,
        temperature_sensor=temperature_sensor,
        humidity_sensor=humidity_sensor,
        soil_moisture_sensor=soil_moisture_sensor,
        threshold_calculator=threshold_calculator,
        soil_type=soiltypes  # Example soil type
    )

    # Calculate and print the watering duration
    watering_duration = watering_calculator.calculate_duration()
    print(f"Watering Duration for {watering_calculator.soil_type} Soil: {watering_duration} minutes")

