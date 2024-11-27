import constants.const as cconst
from fetch_weather_data import WeatherFetcher
from service.decision.mysqptest import const_h


class SoilMoisturePredictor:
    def __init__(self):
        self.soil_absorption_factors = cconst.SOIL_ABSORPTION_FACTOR

    def fetch_forecast_data(self, weather_fetcher):
        """
        Fetches current weather data
        """
        weather_data = weather_fetcher.fetch_current_weather_data()
        rain_amount = weather_data.get("rain_probability", 0)
        return {
            "rain_amount": rain_amount
        }

    def predict_soil_moisture_after_rain(self, current_soil_moisture, forecast_data, soil_type):
        """
        Predicts soil moisture after a rain event based on current conditions and forecast data.
        """
        rain_amount = forecast_data.get("rain_amount", 0)

        # Get soil absorption factor based on soil type
        soil_absorption_factor = self.soil_absorption_factors.get(soil_type, cconst.DEFAULT_SOIL_ABSORPTION_FACTOR) #default value for unknown soil type

        # Calculate increase in soil moisture due to rain
        moisture_increase = rain_amount * soil_absorption_factor

        # Calculate the predicted soil moisture after rain
        predicted_soil_moisture = current_soil_moisture + moisture_increase

        # Full saturation is 1
        predicted_soil_moisture = min(predicted_soil_moisture, 1.0)

        return predicted_soil_moisture
