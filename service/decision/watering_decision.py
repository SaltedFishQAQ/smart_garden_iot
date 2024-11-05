# watering_decision.py

import json
from datetime import datetime, timedelta
from config_loader import load_sensor_config
from fetch_weather_data import WeatherFetcher
from fetch_sensor_data import SoilMoistureSensor, TemperatureSensor, HumiditySensor
from soil_moisture_predictor import SoilMoisturePredictor
from watering_duration import WateringDurationCalculator
from calculate_thresholds import ThresholdCalculator

config = load_sensor_config('sensor_config.xml')


class WateringDecisionMaker:
    def __init__(self, weather_fetcher, soil_moisture_sensor, soil_moisture_predictor,
                 watering_duration_calculator, threshold_calculator, soil_type="Clay"):
        self.weather_fetcher = weather_fetcher
        self.soil_moisture_sensor = soil_moisture_sensor
        self.soil_moisture_predictor = soil_moisture_predictor
        self.watering_duration_calculator = watering_duration_calculator
        self.threshold_calculator = threshold_calculator
        self.soil_type = soil_type
        self.historical_data = self.weather_fetcher.fetch_historical_weather_data()

    def calculate_dynamic_threshold(self):
        print("Calculating dynamic soil moisture threshold based on recent historical data...")

        recent_data = self.historical_data.tail(15)
        avg_temp_24h = recent_data['avg_temp_24h'].mean()
        avg_humidity_24h = recent_data['avg_humidity_24h'].mean()

        print(f"15-day Average Temperature: {avg_temp_24h}")
        print(f"15-day Average Humidity: {avg_humidity_24h}")

        baseline_threshold = self.threshold_calculator.get_daily_threshold(
            datetime.now().strftime('%Y-%m-%d'), soil_type=self.soil_type
        )['soil_moisture_threshold']

        print(f"Baseline Soil Moisture Threshold for {self.soil_type} Soil: {baseline_threshold}")

        adjustment_factor = 1.0

        if avg_temp_24h > 20:
            temperature_factor = 1 - ((avg_temp_24h - 20) / 100)
            adjustment_factor *= temperature_factor
            print(f"Adjusting threshold for temperature: Factor {temperature_factor:.3f}")

        if avg_humidity_24h < 60:
            humidity_factor = 1 - ((60 - avg_humidity_24h) / 100)
            adjustment_factor *= humidity_factor
            print(f"Adjusting threshold for humidity: Factor {humidity_factor:.3f}")

        adjusted_threshold = baseline_threshold * adjustment_factor
        print(f"Adjusted Soil Moisture Threshold for {self.soil_type} Soil: {adjusted_threshold}")
        return adjusted_threshold

    def analyze_conditions(self):
        print("Fetching current weather data...")
        current_weather = self.weather_fetcher.fetch_current_weather_data()
        if not current_weather:
            print("Failed to fetch current weather data.")
            return None

        print(
            f"Current Weather Data:\n  Sunrise: {current_weather['sunrise']}\n  Sunset: {current_weather['sunset']}\n  "
            f"Cloudiness: {current_weather['cloudiness']}%\n  Rain Probability: {current_weather['rain_probability']} mm")

        soil_moisture_threshold = self.calculate_dynamic_threshold()

        print("Fetching current soil moisture reading...")
        soil_moisture_data = json.loads(self.soil_moisture_sensor.monitor())
        current_soil_moisture = float(soil_moisture_data.get('soil_moisture', 0))

        print(f"Current Soil Moisture: {current_soil_moisture}")
        print(f"Soil Moisture Threshold for Decision: {soil_moisture_threshold}")

        rain_probability = current_weather["rain_probability"]
        if rain_probability > 0:
            forecast_data = self.soil_moisture_predictor.fetch_forecast_data(self.weather_fetcher)
            predicted_soil_moisture = self.soil_moisture_predictor.predict_soil_moisture_after_rain(
                current_soil_moisture, forecast_data
            )
            print(f"Predicted Soil Moisture after Rain: {predicted_soil_moisture}")

            if predicted_soil_moisture >= soil_moisture_threshold:
                print("Decision: Skip Watering (Predicted soil moisture after rain is above threshold)")
                return "Skip Watering"

        decision = self.make_decision(current_weather, current_soil_moisture, soil_moisture_threshold)
        return decision

    def make_decision(self, current_weather, current_soil_moisture, soil_moisture_threshold):
        print("Making watering decision based on time, cloudiness, and soil moisture...")

        cloudiness = current_weather["cloudiness"]
        sunrise = datetime.fromisoformat(current_weather["sunrise"])
        sunset = datetime.fromisoformat(current_weather["sunset"])
        now = datetime.now(sunrise.tzinfo)

        print(f"Current Time: {now}")
        print(f"Sunrise: {sunrise}, Sunset: {sunset}")
        print(f"Cloudiness: {cloudiness}%")

        if (sunrise - timedelta(hours=1) <= now <= sunrise + timedelta(hours=1)) or \
                (sunset - timedelta(hours=1) <= now <= sunset + timedelta(hours=1)) or \
                (cloudiness >= 1):
            watering_duration = self.watering_duration_calculator.calculate_duration()
            print(f"Calculated Watering Duration: {watering_duration} minutes")
            if watering_duration > 0:
                print(f"Decision: Watering Required - Duration: {watering_duration} minutes")
                return f"Watering for {watering_duration} minutes"
            else:
                print("Decision: No Watering Required (Environmental conditions do not justify watering)")
                return "No Watering Required"
        else:
            print("Decision: Skip Watering (Not within optimal watering time and conditions)")
            return "Skip Watering"


if __name__ == "__main__":
    current_weather_api_url = "http://ec2-3-79-189-115.eu-central-1.compute.amazonaws.com:5000/weather"
    historical_weather_api_url = config['api_url']
    weather_fetcher = WeatherFetcher(current_weather_api_url, historical_weather_api_url)

    file_path = 'weather_turin.csv'
    soil_type = "Clay"

    threshold_calculator = ThresholdCalculator(file_path, n_estimators=100, window=7)
    soil_moisture_sensor = SoilMoistureSensor(soil_type=soil_type)
    soil_moisture_predictor = SoilMoisturePredictor(soil_absorption_factor=0.7)
    temperature_sensor = TemperatureSensor()
    humidity_sensor = HumiditySensor()
    watering_duration_calculator = WateringDurationCalculator(
        weather_fetcher=weather_fetcher,
        temperature_sensor=temperature_sensor,
        humidity_sensor=humidity_sensor,
        soil_moisture_sensor=soil_moisture_sensor,
        threshold_calculator=threshold_calculator,
        soil_type=soil_type
    )

    decision_maker = WateringDecisionMaker(
        weather_fetcher=weather_fetcher,
        soil_moisture_sensor=soil_moisture_sensor,
        soil_moisture_predictor=soil_moisture_predictor,
        watering_duration_calculator=watering_duration_calculator,
        threshold_calculator=threshold_calculator,
        soil_type=soil_type
    )

    decision = decision_maker.analyze_conditions()
    print(f"Final Decision: {decision}")
