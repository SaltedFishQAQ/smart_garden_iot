# General
REFRESH_TIME = 60

# MQTT Configuration
MQTT_BROKER = "43.131.48.203"
MQTT_PORT = 1883
MQTT_TOPIC = "iot/lwx123321/test/device/command/alerts"

# API Endpoints
OPENWEATHERMAP_API = "https://api.openweathermap.org/data/2.5/weather"
OPENWEATHERMAP_API_KEY = "token"
OPENMETEO_API = "https://api.open-meteo.com/v1/forecast"
SAMPLE_CITY = "London"
SAMPLE_LAT = 51.5074
SAMPLE_LONG = -0.1278

# Database Configuration
MYSQL_CONFIG = {
    "host": "43.131.48.203",
    "port": 3306,
    "user": "username",
    "password": "password.",
    "database": "database_name",
}
INFLUXDB_HOST = "43.131.48.203"
INFLUXDB_PORT = 18086

# Thresholds (percentage)
CPU_THRESHOLD = 80
RAM_THRESHOLD = 90

# Web Server Configuration
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 8080

# Docker server configuration
IP_SERVER = "43.131.48.203"
