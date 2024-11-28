IoT Monitoring Service

The Service is a critical component of the IoT Smart Garden system, responsible for ensuring the health and reliability of all connected devices and services. It integrates with Docker, MQTT, and Telegram bot notifications to provide real-time updates and alerts on system performance and failures.

Features
•	Real-Time Monitoring: Tracks the status of Docker containers, databases, and external APIs.
•	Container Health Check:
    o	Monitors container states (running/stopped).
    o	Checks CPU and memory usage, sending alerts when thresholds are exceeded.
•	Database Monitoring:
    o	Ensures MySQL and InfluxDB databases are operational and accessible.
•	API Monitoring:
    o	Validates external weather API functionality (e.g., Open-Meteo, OpenWeatherMap).
•	MQTT Integration: Publishes alerts to a predefined topic for system-wide communication.
•	Telegram Bot Integration:
    o	Sends real-time alerts for critical issues like container failures or database inaccessibility.
    o	Updates users on the overall health of the system through commands.
•	Web Dashboard:
    o	Provides a user-friendly interface to view container statuses, resource usage, and system performance.

File Structure
•	monitoring.py: Main service that monitors containers, databases, and APIs, and sends alerts.
•	web-main.py: Hosts the monitoring dashboard, displaying real-time component statuses.
•	constant_values.py: Defines configurable thresholds (CPU/memory usage), MQTT topics, and monitoring intervals.
•	plain_text.html: HTML template for the web dashboard.
•	requirements.txt: Python dependencies required for running the monitoring service.
•	Dockerfile: Docker configuration for deploying the monitoring service in a container.

Telegram Bot Commands
The Monitoring Service integrates with the Telegram bot to provide updates:
•	Alerts: Sends immediate notifications for:
    o	Docker container failures.
    o	Database or API unavailability.
    o	Resource usage exceeding thresholds.
•	Status Summary: Provides a detailed report of system health upon user request.

Setup
Prerequisites
•	Python (Version 3.8+)
•	Docker and Docker-Compose
•	MQTT Broker (e.g., Mosquitto)
•	Telegram Bot Token for notifications.

‘‘’bash
git clone https://github.com/SaltedFishQAQ/smart_garden_iot.git
cd smart_garden_iot/third_party/monitoring
python monitoring.py
docker build -t monitoring_service .
docker-compose up -d
