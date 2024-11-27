import constants.const as const

soil_types = const.SOIL_TYPE

class WateringDurationCalculator:
    def __init__(self, weather_fetcher, threshold_calculator, soil_type, base_duration=15):
        self.weather_fetcher = weather_fetcher
        self.threshold_calculator = threshold_calculator
        self.base_duration = base_duration
        self.soil_type = soil_type
        self.adjustment_factor = soil_types[soil_type]["adjustment_factor"]

    def calculate_duration(self, soil_moisture, threshold):
        """
        Calculate the watering duration based on soil moisture, temperature, humidity, and rain data.
        """

        # Fetch rain probability from the weather fetcher
        current_weather = self.weather_fetcher.fetch_current_weather_data()
        rain_mm = float(current_weather.get("rain_probability", 0))

        #water requirment calculation
        moisture_deficit = (threshold * 100) - (soil_moisture * 100)
        required_water = (moisture_deficit * const.DEPTH * const.DENSITY * const.CUBIC_AREA) / 100
        water_adjustment = required_water * self.adjustment_factor
        rain_adjustment = rain_mm * const.CUBIC_AREA * self.adjustment_factor

        # Calculate total watering duration
        print(f"required_water: {required_water}, rain_adjustment: {rain_adjustment}")
        duration = (water_adjustment - rain_adjustment) / const.VALVE_FLOW_RATE
        return max(0, duration)
