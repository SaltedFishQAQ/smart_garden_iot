import sys
import json
import constants.const as const
import constants.http as chttp
from datetime import datetime, timedelta
from fetch_weather_data import WeatherFetcher
from fetch_sensor_data import SensorDataFetcher
from soil_moisture_predictor import SoilMoisturePredictor
from watering_duration import WateringDurationCalculator
from calculate_thresholds import ThresholdCalculator
import paho.mqtt.client as mqtt
import time
import logging
from logging.handlers import SysLogHandler

# Configure syslog
import logging
from concurrent_log_handler import ConcurrentRotatingFileHandler

# Configure logging
log_file = '/tmp/decision_service.log'
handler = ConcurrentRotatingFileHandler(log_file, maxBytes= const.MAX_BYTES)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - [%(process)d] %(message)s')
handler.setFormatter(formatter)

logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


# MQTT settings
BROKER_ADDRESS = chttp.BROKER_ADDRESS
BROKER_PORT = chttp.BROKER_PORT
BASE_TOPIC = const.MESSAGE_BROKER_BASE_PATH + const.WATERING_TOPIC_BASE_PATH


class WateringDecisionMaker:
    def __init__(self, weather_fetcher, sensor_fetcher, soil_moisture_predictor,
                 watering_duration_calculator, threshold_calculator, area, soil_type):
        self.weather_fetcher = weather_fetcher
        self.sensor_fetcher = sensor_fetcher
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

        # Fetch baseline threshold based on soil type
        baseline_threshold = self.threshold_calculator.get_daily_threshold(
            datetime.now().strftime('%Y-%m-%d'), soil_type=self.soil_type
        )['soil_moisture_threshold']

        adjustment_factor = const.DEFAULT_ADJUSTMENT_FACTOR
        if avg_temp_24h > const.BASELINE_TEMP_FOR_ADJUSTMENT:
            temperature_factor = 1 - (
                (avg_temp_24h - const.BASELINE_TEMP_FOR_ADJUSTMENT) * const.TEMP_ADJUSTMENT_FACTOR
            )
            adjustment_factor *= temperature_factor

        if avg_humidity_24h < const.BASELINE_HUMIDITY_FOR_ADJUSTMENT:
            humidity_factor = 1 - (
                (const.BASELINE_HUMIDITY_FOR_ADJUSTMENT - avg_humidity_24h) * const.HUMIDITY_ADJUSTMENT_FACTOR
            )
            adjustment_factor *= humidity_factor

        adjusted_threshold = baseline_threshold * adjustment_factor

        logger.info(f"Predicted Threshold (pre-adjustment): {baseline_threshold}")
        logger.info(f"Adjusted Threshold for {self.soil_type} soil: {adjusted_threshold}")
        return adjusted_threshold

    def analyze_conditions(self):
        current_weather = self.weather_fetcher.fetch_current_weather_data()
        if not current_weather:
            logger.error(f"Failed to fetch current weather data for {self.area}.")
            return "Skip Watering"

        # Fetch sensor data
        humidity, temperature, current_soil_moisture = self.sensor_fetcher.get_sensor_data(self.area)
        logger.info(f"Humidity: {humidity}%, Temperature: {temperature}, Soil Moisture: {current_soil_moisture}")
        if humidity is None and temperature is None and current_soil_moisture is None:
            logger.error(f"Failed to fetch sensor data for {self.area}.")
            return "Skip Watering"

        soil_moisture_threshold = self.calculate_dynamic_threshold()

        rain_probability = current_weather["rain_probability"]
        if rain_probability > const.MIN_RAIN_PROBABILITY:
            forecast_data = self.soil_moisture_predictor.fetch_forecast_data(self.weather_fetcher)
            predicted_soil_moisture = self.soil_moisture_predictor.predict_soil_moisture_after_rain(
                current_soil_moisture, forecast_data, soil_type
            )
            if predicted_soil_moisture >= soil_moisture_threshold:
                return "Skip Watering"

        decision = self.make_decision(current_weather, current_soil_moisture)
        return decision

    def make_decision(self, current_weather, current_soil_moisture):
        cloudiness = current_weather["cloudiness"]
        sunrise = datetime.fromisoformat(current_weather["sunrise"])
        sunset = datetime.fromisoformat(current_weather["sunset"])
        now = datetime.now(sunrise.tzinfo)

        if (now <= sunrise + timedelta(hours=1) or now >= sunset - timedelta(hours=1)) or \
                (cloudiness >= const.MIN_CLOUDINESS_FOR_WATERING):
            watering_duration = self.watering_duration_calculator.calculate_duration(
                current_soil_moisture, self.calculate_dynamic_threshold()
            )
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
        logger.info(
            f"Sent {'start' if status else 'stop'} watering command to {topic} for duration {duration} seconds." if duration else "until stopped."
        )

        if status:
            time.sleep(duration)  # Wait for the duration of watering
            self.send_mqtt_command(False)  # Send stop command after duration
        client.disconnect()


def main(area, soil_type):
    weather_fetcher = WeatherFetcher()
    sensor_fetcher = SensorDataFetcher()
    threshold_calculator = ThresholdCalculator()
    soil_moisture_predictor = SoilMoisturePredictor()

    # Initialize WateringDurationCalculator
    watering_duration_calculator = WateringDurationCalculator(
        weather_fetcher=weather_fetcher,
        threshold_calculator=threshold_calculator,
        soil_type=soil_type
    )

    decision_maker = WateringDecisionMaker(
        weather_fetcher=weather_fetcher,
        sensor_fetcher=sensor_fetcher,
        soil_moisture_predictor=soil_moisture_predictor,
        watering_duration_calculator=watering_duration_calculator,
        threshold_calculator=threshold_calculator,
        area=area,
        soil_type=soil_type
    )

    decision = decision_maker.analyze_conditions()
    logger.info(f"Final Decision for {area}: {decision}")

    if decision.startswith("Watering for"):
        duration = float(decision.split()[2]) * 60
        decision_maker.send_mqtt_command(True, duration)  # Start watering with specified duration


if __name__ == "__main__":
    if len(sys.argv) != 3:
        logger.info("Usage: python watering_decision.py <area> <soil_type>")
        sys.exit(1)

    area = sys.argv[1]
    soil_type = sys.argv[2]

    main(area, soil_type)
