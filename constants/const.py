
MESSAGE_BROKER_BASE_PATH = "iot/lwx123321/test/"


# Watering Decision Making
DEFAULT_SOIL_TYPE = "Clay"
WATERING_TOPIC_BASE_PATH = 'device/command/irrigator/'
CSV_FILE_PATH = 'weather_turin.csv'
MIN_RAIN_PROBABILITY = 1.0
MIN_CLOUDINESS_FOR_WATERING = 80
from datetime import timedelta
WATERING_TIME_WINDOW = timedelta(hours=1)
DEFAULT_ADJUSTMENT_FACTOR = 1.1
SOIL_ABSORPTION_FACTOR = {
    "Sandy": "0.85",
    "Clay": "0.3",
    "Loamy": "0.7",
    "Silty": "0.6",
    "Peaty": "0.8"
}
DEFAULT_SOIL_ABSORPTION_FACTOR = 0.5
TEMP_ADJUSTMENT_FACTOR = 0.02
BASELINE_TEMP_FOR_ADJUSTMENT = 20
HUMIDITY_ADJUSTMENT_FACTOR = 0.01
BASE_WATERING_DURATION = 15
TEMP_THRESHOLD = 25
HUMIDITY_THRESHOLD = 40
BASELINE_HUMIDITY_FOR_ADJUSTMENT = 60

SOIL_TYPE = {
    "Sandy": {"field_capacity": 15, "wilting_point": 4, "adjustment_factor": 0.3},
    "Clay": {"field_capacity": 50, "wilting_point": 15, "adjustment_factor": 1.0},  # Default base
    "Loamy": {"field_capacity": 25, "wilting_point": 10, "adjustment_factor": 0.85},
    "Silty": {"field_capacity": 35, "wilting_point": 12, "adjustment_factor": 0.9},
    "Peaty": {"field_capacity": 40, "wilting_point": 10, "adjustment_factor": 0.88},
}


#Watering_coordinator
CHECK_INTERVAL = 20
RUNNING_CHECK_INTERVAL = 2

#Watering Duration (based on garden characteristics)
DEPTH = 0.3
DENSITY = 1300
CUBIC_AREA = 50
VALVE_FLOW_RATE = 30*60

#logging
MAX_BYTES = 5_000_000