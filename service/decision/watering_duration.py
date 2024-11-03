import json
from fetch_weather_data import WeatherFetcher
from fetch_sensor_data import TemperatureSensor, HumiditySensor, SoilMoistureSensor


class WateringDurationCalculator:
    def __init__(self, weather_fetcher, temperature_sensor, humidity_sensor, soil_moisture_sensor,
                 base_duration=15, soil_moisture_threshold=0.3, temp_threshold=25, humidity_threshold=40):
        """
        Initializes the WateringDurationCalculator with thresholds and sensors for real-time data.

        Parameters:
            weather_fetcher (WeatherFetcher): Instance of WeatherFetcher to get rain and cloud data.
            temperature_sensor (TemperatureSensor): Instance of TemperatureSensor for temperature data.
            humidity_sensor (HumiditySensor): Instance of HumiditySensor for humidity data.
            soil_moisture_sensor (SoilMoistureSensor): Instance of SoilMoistureSensor for soil moisture data.
            base_duration (int): Base watering duration in minutes.
            soil_moisture_threshold (float): Soil moisture threshold for adjusting watering.
            temp_threshold (int): Temperature threshold for adjusting watering.
            humidity_threshold (int): Humidity threshold for adjusting watering.
        """
        self.weather_fetcher = weather_fetcher
        self.temperature_sensor = temperature_sensor
        self.humidity_sensor = humidity_sensor
        self.soil_moisture_sensor = soil_moisture_sensor
        self.base_duration = base_duration
        self.soil_moisture_threshold = soil_moisture_threshold
        self.temp_threshold = temp_threshold
        self.humidity_threshold = humidity_threshold

    def calculate_duration(self):
        """
        Calculate the watering duration based on sensor and weather data.

        Returns:
            int: Calculated watering duration in minutes.
        """
        # Fetch sensor data and parse the JSON strings into dictionaries
        soil_moisture_data = json.loads(self.soil_moisture_sensor.monitor())
        temperature_data = json.loads(self.temperature_sensor.monitor())
        humidity_data = json.loads(self.humidity_sensor.monitor())

        # Fetch weather data (rain amount in mm)
        weather_data = self.weather_fetcher.fetch_weather_data()

        # Parse the values from the fetched data
        soil_moisture = float(soil_moisture_data.get('soil_moisture', 0))
        temperature = float(temperature_data.get('temperature', 0))
        humidity = float(humidity_data.get('humidity', 0))
        rain_mm = float(weather_data.get("rain_probability", 0))  # Rain amount in mm

        # Calculate adjustments for each factor
        moisture_adjustment = max(0, (
                    self.soil_moisture_threshold - soil_moisture) * 50)  # Each 0.1 m³/m³ below threshold adds 5 minutes
        temp_adjustment = max(0, (temperature - self.temp_threshold) * 2)  # Each degree above threshold adds 2 minutes
        humidity_adjustment = max(0,
                                  (self.humidity_threshold - humidity) * 0.5)  # Each % below threshold adds 0.5 minutes
        rain_adjustment = rain_mm * 5  # Each mm of rain reduces watering by 5 minutes

        # Calculate total watering duration
        duration = self.base_duration + moisture_adjustment + temp_adjustment + humidity_adjustment - rain_adjustment
        return max(0, duration)  # Ensure non-negative duration


# Example usage
if __name__ == "__main__":
    # Initialize instances of WeatherFetcher and sensors
    api_url = "http://ec2-3-79-189-115.eu-central-1.compute.amazonaws.com:5000/weather"
    weather_fetcher = WeatherFetcher(api_url)

    # Initialize sensors with sensor types
    temperature_sensor = TemperatureSensor()
    humidity_sensor = HumiditySensor()
    soil_moisture_sensor = SoilMoistureSensor(soil_type="clay")

    # Initialize the WateringDurationCalculator with all required instances
    watering_calculator = WateringDurationCalculator(
        weather_fetcher=weather_fetcher,
        temperature_sensor=temperature_sensor,
        humidity_sensor=humidity_sensor,
        soil_moisture_sensor=soil_moisture_sensor
    )

    # Calculate and print the watering duration
    watering_duration = watering_calculator.calculate_duration()
    print(f"Watering Duration: {watering_duration} minutes")
