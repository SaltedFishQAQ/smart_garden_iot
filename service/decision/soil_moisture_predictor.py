from fetch_weather_data import WeatherFetcher

class SoilMoisturePredictor:

    def __init__(self, soil_absorption_factor=0.7):

        self.soil_absorption_factor = soil_absorption_factor

    def fetch_forecast_data(self, weather_fetcher):
        """
        Fetches weather data from an external weather API using a provided WeatherFetcher instance.
        Parameters:
            weather_fetcher (WeatherFetcher): An instance of WeatherFetcher to get forecast data.
        Returns:
            dict: Contains forecast data with key 'rain_amount' in mm.
        """
        weather_data = weather_fetcher.fetch_weather_data()

        rain_amount = weather_data.get("rain_probability", 0)

        return {
            "rain_amount": rain_amount
        }

    def predict_soil_moisture_after_rain(self, current_soil_moisture, forecast_data):
        """
        Predicts soil moisture after a rain event based on current conditions and forecast data.

        Parameters:
            current_soil_moisture (float): The current soil moisture level.
            forecast_data (dict): Contains 'rain_amount' in mm.

        Returns:
            float: Predicted soil moisture level after rain.
        """
        rain_amount = forecast_data.get("rain_amount", 0)

        # Check if there is a significant rain amount
        if rain_amount <= 0:
            print("No significant rain amount; soil moisture remains unchanged.")
            return current_soil_moisture

        # Calculate increase in soil moisture due to rain
        moisture_increase = rain_amount * self.soil_absorption_factor

        # Calculate the predicted soil moisture after rain
        predicted_soil_moisture = current_soil_moisture + moisture_increase

        #full saturation is 1
        predicted_soil_moisture = min(predicted_soil_moisture, 1.0)

        return predicted_soil_moisture

if __name__ == "__main__":
    soil_moisture_predictor = SoilMoisturePredictor(soil_absorption_factor=0.7)

    current_soil_moisture = 0.4

    api_url = "http://ec2-3-79-189-115.eu-central-1.compute.amazonaws.com:5000/weather"
    weather_fetcher = WeatherFetcher(api_url)

    forecast_data = soil_moisture_predictor.fetch_forecast_data(weather_fetcher)

    predicted_soil_moisture = soil_moisture_predictor.predict_soil_moisture_after_rain(
        current_soil_moisture, forecast_data
    )

    print(f"Predicted Soil Moisture After Rain: {predicted_soil_moisture:.3f}")
