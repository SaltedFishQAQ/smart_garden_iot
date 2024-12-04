# IoT Bot Notification System

A Telegram bot integrated with MQTT and HTTP APIs to control an IoT system. This bot allows users to monitor environmental factors such as temperature, humidity, and control devices like lights and watering systems in a smart garden. It also supports user authentication and provides a notification system.

## Features

- **User Authentication**: Users must authenticate with a username and password to access the bot's features. The token of authenticated user with their role in the system kept to authorize their action. Admin can see sensor values and status of all the area. see control buttom and trigger them while user only can see dedicated areas with no control action permitted by the system for normal user.
- **Real-time Notifications**: Registered users receive updates and alerts regarding infrastructure adn API statuses.
- **MQTT Integration**: Communicates with devices using MQTT to control the light and watering systems.
- **REST API Integration**: Fetches sensor data and rules from an HTTP API for temperature, humidity, and device statuses.
- **Plant Identification**: Users can identify a plant by sending a photo. The bot sends the image to the Plant.ID API and returns information such as the plant’s name, taxonomy, description, and similar images.
- **Customizable Rules**: Allows users to view rules for automated actions based on environmental conditions.
- **Telegram Bot Commands**:
  - `/start`: Authenticate and access the bot menu.
  - `/stop`: Logout and need to login again to use BOT
  - **Main Menu**:
    - **Temperature**: View recent temperature readings for dedicated areas
    - **Humidity**: View recent humidity readings for dedicated areas
    - **Soli Moisture**: View recent soil moisture readings for dedicated areas
    - **Light**: Control the garden light (turn on/off). (Only admin can trigger)
    - **Watering**: Control the watering system (turn on/off). (Only admin can trigger)
    - **View Rules**: Display active rules for automated actions.
    - **Status**: Get the current system status (temperature, humidity, light, oxygen, soil sensor and actuators).
    - **Identify Plant**: Send a plant photo to identify the species and retrieve details such as common names and similar images.

## File Structure

- **`bot.py`**: Main bot application with command handling.
- **`mqtt.py`**: Handles all MQTT communication, including subscribing to topics, publishing messages, and handling reconnections.
- **`notification.py`**: Manages user notifications and sends updates to all subscribed users.
- **`authenticator.py`**: Handles user authentication with the server.
- **`plant.py`**: Handles plant identification by sending photos to the Plant.ID API.
- **`config.xml`**: Configuration file storing server API endpoints, bot token, and MQTT settings.
- **`requirements.txt`**: Python dependencies for the project.
- **`Dockerfile`**: Docker configuration for setting up and running the bot in a container.

## Setup

1. Clone this repository:
   ```bash
   git clone https://github.com/SaltedFishQAQ/smart_garden_iot.git
   cd smart_garden_iot/third_party/telebot

