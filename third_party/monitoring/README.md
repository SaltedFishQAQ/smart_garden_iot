# IoT Monitoring Service

The IoT Monitoring Service is a critical component of the **IoT Smart Garden** system, designed to ensure the health and reliability of connected devices and services. It integrates Docker, MQTT, and Telegram bot notifications to deliver real-time updates and alerts about system performance and potential failures.

## Features

- **Real-Time Monitoring:**
  - Tracks the status of Docker containers, databases, and external APIs.
- **Container Health Check:**
  - Monitors container states (running/stopped).
  - Tracks CPU and memory usage, sending alerts when thresholds are exceeded.
- **Database Monitoring:**
  - Ensures MySQL and InfluxDB databases are operational and accessible.
- **API Monitoring:**
  - Validates external weather API functionality (e.g., Open-Meteo, OpenWeatherMap).
- **MQTT Integration:**
  - Publishes alerts to a predefined topic for system-wide communication.
- **Telegram Bot Integration:**
  - Sends real-time alerts for critical issues like container failures or database inaccessibility.
- **Web Dashboard:**
  - Displays real-time statuses of containers, resource usage, and overall system performance.

## File Structure

- **`monitoring.py`**: Main service that monitors containers, databases, and APIs, and sends alerts.
- **`web-main.py`**: Hosts the monitoring dashboard, displaying real-time component statuses.
- **`constant_values.py`**: Defines configurable thresholds (CPU/memory usage), MQTT topics, and monitoring intervals.
- **`plain_text.html`**: HTML template for the web dashboard.
- **`requirements.txt`**: Python dependencies required for running the monitoring service.
- **`Dockerfile`**: Docker configuration for deploying the monitoring service in a container.

## Telegram Bot Commands

The service integrates with Telegram bots to provide system updates:
- **Alerts:**
  - Immediate notifications for:
    - Docker container failures.
    - Database or API unavailability.
    - Resource usage exceeding thresholds.

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/SaltedFishQAQ/smart_garden_iot.git
   cd smart_garden_iot/third_party/monitoring
