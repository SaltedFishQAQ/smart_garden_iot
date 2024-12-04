# Smart Garden IoT: Weather Microservice

This is a Weather Microservice for the **Smart Garden IoT** system, which interacts with the OpenWeatherMap and OpenMeteo API to fetch current and forecasted weather data (such as temperature, humidity, wind speed, sunrise, sunset, and rain probability) and historical data for system management and decision making. It provides parsed weather data that can be used for automating tasks like turning lights on or off during sunrise/sunset and managing irrigation systems based on rain forecasts and historical weather pattern.

## Features

- Fetches weather data from the OpenWeatherMap API:
  - **Temperature**
  - **Humidity**
  - **Wind Speed**
  - **Rain Probability**
  - **Sunrise and Sunset Times**
  - **Description**
  - **Cloud Cover**
  - **Air pressure**
- Fetches historical weather data from the OpenMeteo API for decision manipulation:
  - **Humidity**
  - **Temperature**
  - **precipitation**

- Modular design to simplify fetching and parsing weather data.
- Parses and returns weather data in a structured format.

## File Structure

- **`weather_adapter.py`**: adapter exposes the fetch data.
- **`data.py`**: Parses and processes the weather data fetched from the OpenWeatherMap API and OpenMeteo
- **`weather_config.xml`**: Configuration file that stores API URL, API key, city for weather data, and the timezone for processing sunrise/sunset times.
- **`requirements.txt`**: Lists the Python dependencies required for the project.

## Setup

1. Clone this repository:
   ```bash
   git clone https://github.com/SaltedFishQAQ/smart_garden_iot.git
   cd smart_garden_iot/third_party/weather

