## Monitoring Service Updates

- **Monitoring Features**:
  - Monitors InfluxDB and MySQL for availability.
  - Tracks Docker container resource usage and health.
  - Sends real-time alerts via Telegram Bot.

- **How It Works**:
  - The monitoring service collects metrics from databases, APIs, and Docker containers.
  - Real-time alerts notify users of any failures or performance bottlenecks.

- **To Start the Monitoring Service**:
  1. Run `docker-compose up -d` to start all services.
  2. Access the monitoring dashboard at `51.20.82.208:8080`
