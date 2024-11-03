
class WateringDurationCalculator:
    def __init__(self, base_duration=15, soil_moisture_threshold=0.3, temp_threshold=25, humidity_threshold=40):
        self.base_duration = base_duration
        self.soil_moisture_threshold = soil_moisture_threshold
        self.temp_threshold = temp_threshold
        self.humidity_threshold = humidity_threshold

    def calculate_duration(self, soil_moisture, temperature, humidity, rain_mm):
        # Soil moisture adjustment
        moisture_adjustment = max(0, (self.soil_moisture_threshold - soil_moisture) * 50)  # each 0.1 m³/m³ below threshold adds 5 minutes

        # Temperature and humidity adjustment
        temp_adjustment = max(0, (temperature - self.temp_threshold) * 2)  # each degree above threshold adds 2 minutes
        humidity_adjustment = max(0, (self.humidity_threshold - humidity) * 0.5)  # each % below threshold adds 0.5 minutes

        # Rain adjustment
        rain_adjustment = rain_mm * 5  # 1 mm rain reduces watering by 5 minutes

        # Calculate total watering duration
        duration = self.base_duration + moisture_adjustment + temp_adjustment + humidity_adjustment - rain_adjustment

        # Duration will not get negative value
        return max(0, duration)


#testing
soil_moisture = 0.25  # Current soil moisture level
temperature = 28  # Current temperature in °C
humidity = 35  # Current humidity in %
rain_mm = 0  # Recent rainfall in mm

water_calculation = WateringDurationCalculator()

watering_duration = water_calculation.calculate_duration(
    soil_moisture=soil_moisture,
    temperature=temperature,
    humidity=humidity,
    rain_mm=rain_mm
)

print(f"Watering Duration: {watering_duration} minutes")
