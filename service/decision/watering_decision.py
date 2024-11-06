import sys
import json
import constants.const as const
from datetime import datetime, timedelta
from config_loader import load_sensor_config
from fetch_weather_data import WeatherFetcher
from fetch_sensor_data import SoilMoistureSensor, TemperatureSensor, HumiditySensor
from soil_moisture_predictor import SoilMoisturePredictor
from watering_duration import WateringDurationCalculator
from calculate_thresholds import ThresholdCalculator
import paho.mqtt.client as mqtt
import time

config = load_sensor_config('sensor_config.xml')

# MQTT settings
BROKER_ADDRESS = "43.131.48.203"
BROKER_PORT = 1883
BASE_TOPIC = const.MESSAGE_BROKER_BASE_PATH + const.WATERING_TOPIC_BASE_PATH

class WateringDecisionMaker:
    def __init__(self, weather_fetcher, soil_moisture_sensor, soil_moisture_predictor,
                 watering_duration_calculator, threshold_calculator, area, soil_type):
        self.weather_fetcher = weather_fetcher
        self.soil_moisture_sensor = soil_moisture_sensor
        self.soil_moisture_predictor = soil_moisture_predictor
        self.watering_duration_calculator = watering_duration_calculator
        self.threshold_calculator = threshold_calculator
        self.area = area
        self.soil_type = soil_type
        self.historical_data = self.weather_fetcher.fetch_historical_weather_data()

    def calculate_dynamic_threshold(self):
        recent_data = self.historical_data.tail(15)
        avg_temp_24h = recent_data['avg_temp_24h'].mean()
        avg_humidity_24h = recent_data['avg_humidity_24h'].mean()

        # Fetch baseline threshold based on the correct soil type
        baseline_threshold = self.threshold_calculator.get_daily_threshold(
            datetime.now().strftime('%Y-%m-%d'), soil_type=self.soil_type
        )['soil_moisture_threshold']

        adjustment_factor = const.DEFAULT_ADJUSTMENT_FACTOR
        if avg_temp_24h > const.BASELINE_TEMP_FOR_ADJUSTMENT:
            temperature_factor = 1 - (
                        (avg_temp_24h - const.BASELINE_TEMP_FOR_ADJUSTMENT) * const.TEMP_ADJUSTMENT_FACTOR)
            adjustment_factor *= temperature_factor

        if avg_humidity_24h < const.BASELINE_HUMIDITY_FOR_ADJUSTMENT:
            humidity_factor = 1 - (
                        (const.BASELINE_HUMIDITY_FOR_ADJUSTMENT - avg_humidity_24h) * const.HUMIDITY_ADJUSTMENT_FACTOR)
            adjustment_factor *= humidity_factor

        adjusted_threshold = baseline_threshold * adjustment_factor

        # Print dynamically adjusted messages for the soil type
        print(f"Predicted Threshold (pre-adjustment): {baseline_threshold}")
        print(f"Adjusted Threshold based on {self.soil_type} soil: {adjusted_threshold}")
        return adjusted_threshold

    def analyze_conditions(self):
        current_weather = self.weather_fetcher.fetch_current_weather_data()
        if not current_weather:
            print(f"Failed to fetch current weather data for {self.area}.")
            return "Skip Watering"

        soil_moisture_threshold = self.calculate_dynamic_threshold()
        soil_moisture_data = json.loads(self.soil_moisture_sensor.monitor())
        current_soil_moisture = float(soil_moisture_data.get('soil_moisture', 0))

        rain_probability = current_weather["rain_probability"]
        if rain_probability > const.MIN_RAIN_PROBABILITY:
            forecast_data = self.soil_moisture_predictor.fetch_forecast_data(self.weather_fetcher)
            predicted_soil_moisture = self.soil_moisture_predictor.predict_soil_moisture_after_rain(
                current_soil_moisture, forecast_data
            )
            if predicted_soil_moisture >= soil_moisture_threshold:
                return "Skip Watering"

        decision = self.make_decision(current_weather, current_soil_moisture, soil_moisture_threshold)
        return decision

    def make_decision(self, current_weather, current_soil_moisture, soil_moisture_threshold):
        cloudiness = current_weather["cloudiness"]
        sunrise = datetime.fromisoformat(current_weather["sunrise"])
        sunset = datetime.fromisoformat(current_weather["sunset"])
        now = datetime.now(sunrise.tzinfo)

        if (sunrise - const.WATERING_TIME_WINDOW <= now <= sunrise + const.WATERING_TIME_WINDOW) or \
                (sunset - const.WATERING_TIME_WINDOW <= now <= sunset + const.WATERING_TIME_WINDOW) or \
                (cloudiness >= const.MIN_CLOUDINESS_FOR_WATERING):
            watering_duration = self.watering_duration_calculator.calculate_duration()
            if watering_duration > 0:
                return f"Watering for {watering_duration} minutes"
            else:
                return "No Watering Required"
        else:
            return "Skip Watering"

    def send_mqtt_command(self, status, duration=None):
        client = mqtt.Client()
        client.connect(BROKER_ADDRESS, BROKER_PORT, 60)

        command = {"type": "opt", "status": status}
        topic = f"{BASE_TOPIC}{self.area}"

        client.publish(topic, payload=json.dumps(command), qos=1)
        print(
            f"Sent {'start' if status else 'stop'} watering command to {topic} for duration {duration} seconds." if duration else "until stopped.")

        if status:
            time.sleep(duration)  # Wait for the duration of watering
            self.send_mqtt_command(False)  # Send stop command after duration
        client.disconnect()


def main(area, soil_type):
    weather_fetcher = WeatherFetcher(
        current_api_url="http://ec2-3-79-189-115.eu-central-1.compute.amazonaws.com:5000/weather",
        historical_api_url=config['api_url']
    )
    threshold_calculator = ThresholdCalculator('weather_turin.csv', n_estimators=100, window=7)
    soil_moisture_sensor = SoilMoistureSensor(soil_type=soil_type)
    soil_moisture_predictor = SoilMoisturePredictor(soil_absorption_factor=const.SOIL_ABSORPTION_FACTOR)
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
        area=area,
        soil_type=soil_type
    )

    decision = decision_maker.analyze_conditions()
    print(f"Final Decision for {area}: {decision}")

    if decision.startswith("Watering for"):
        duration = float(decision.split()[2]) * 60  # Convert minutes to seconds
        decision_maker.send_mqtt_command(True, duration)  # Start watering with specified duration


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python watering_decision.py <area> <soil_type>")
        sys.exit(1)

    area = sys.argv[1]
    soil_type = sys.argv[2]

    main(area, soil_type)
