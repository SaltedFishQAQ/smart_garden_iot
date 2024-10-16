# IoT Bot Notification System

A Telegram bot integrated with MQTT and HTTP APIs to control an IoT system. This bot allows users to monitor environmental factors such as temperature, humidity, and control devices like lights and watering systems in a smart garden. It also supports user authentication and provides a notification system.

## Features

- **User Authentication**: Users must authenticate with a username and password to access the bot's features.
- **Real-time Notifications**: Registered users receive periodic updates and alerts regarding IoT device statuses.
- **MQTT Integration**: Communicates with devices using MQTT to control the light and watering systems.
- **REST API Integration**: Fetches sensor data and rules from an HTTP API for temperature, humidity, and device statuses.
- **Customizable Rules**: Allows users to view rules for automated actions based on environmental conditions.
- **Telegram Bot Commands**:
  - `/start`: Authenticate and access the bot menu.
  - **Main Menu**:
    - **Temperature**: View recent temperature readings.
    - **Humidity**: View recent humidity readings.
    - **Light**: Control the garden light (turn on/off).
    - **Watering**: Control the watering system (turn on/off).
    - **View Rules**: Display active rules for automated actions.
    - **Status**: Get the current system status (temperature, humidity, light, oxygen).

## File Structure

- **`bot.py`**: Main bot application with command handling and MQTT communication.
- **`mqtt.py`**: Handles all MQTT communication, including subscribing to topics, publishing messages, and handling reconnections.
- **`notification.py`**: Manages user notifications and sends updates to all subscribed users.
- **`authenticator.py`**: Handles user authentication with the server.
- **`config.xml`**: Configuration file storing server API endpoints, bot token, and MQTT settings.
- **`requirements.txt`**: Python dependencies for the project.

## Setup

1. Clone this repository:
   ```bash
   git clone https://github.com/SaltedFishQAQ/smart_garden_iot.git
   cd smart_garden_iot/third_party/telebot

