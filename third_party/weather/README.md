# Smart Garden IoT: Weather Microservice

This is a Weather Microservice for the **Smart Garden IoT** system, which interacts with the OpenWeatherMap API to fetch weather data (such as sunrise, sunset, and rain probability) and uses MQTT to communicate with other components like lights and the irrigation system.

This service helps in automating tasks based on weather data, such as turning lights on or off during sunset/sunrise and managing the irrigation system based on rain predictions.

## Features

- Fetches weather data (sunrise, sunset, rain probability) from the OpenWeatherMap API.
- Triggers actions such as turning on/off lights based on sunrise and sunset times.
- Manages the irrigation system based on rain probability (closes the irrigation system if rain is expected).
- Publishes MQTT messages to specific channels to trigger actions in other IoT devices.
- Continuously monitors and updates weather information at configurable intervals.

## File Structure

- **`openweathermap.py`**: Main microservice
- **`weather_config.py`**: Configuration file storing server API endpoints, API key, and MQTT settings.
- **`requirements.txt`**: Python dependencies for the project.

## Setup

1. Clone this repository:
   ```bash
   git clone https://github.com/SaltedFishQAQ/smart_garden_iot.git
   cd smart_garden_iot/third_party/weather

