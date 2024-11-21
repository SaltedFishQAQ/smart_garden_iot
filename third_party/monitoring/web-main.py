import cherrypy
from datetime import datetime
from threading import Thread, Event
from time import sleep
from monitoring import DockerMonitor, APIHealthMonitor, DatabaseHealthMonitor
import paho.mqtt.client as mqtt
import json
from constant_values import (
    REFRESH_TIME,
    MQTT_BROKER,
    MQTT_PORT,
    MQTT_TOPIC,
    OPENWEATHERMAP_API_KEY,
    MYSQL_CONFIG,
    INFLUXDB_HOST,
    INFLUXDB_PORT,
    CPU_THRESHOLD,
    RAM_THRESHOLD,
    SERVER_HOST,
    SERVER_PORT,
)


class IoTMonitoringWebApp:
    def __init__(self):
        self.server_ip = MQTT_BROKER
        self.openweathermap_api_key = OPENWEATHERMAP_API_KEY
        self.mysql_config = MYSQL_CONFIG
        self.influxdb_host = INFLUXDB_HOST
        self.influxdb_port = INFLUXDB_PORT

        self.mqtt_broker = MQTT_BROKER
        self.mqtt_port = MQTT_PORT
        self.mqtt_topic = MQTT_TOPIC
        self.mqtt_client = mqtt.Client()

        try:
            self.mqtt_client.connect(self.mqtt_broker, self.mqtt_port)
            self.mqtt_client.loop_start()
            print(f"Connected to MQTT broker at {self.mqtt_broker}:{self.mqtt_port}")
        except Exception as e:
            print(f"Error connecting to MQTT broker: {e}")

        self.docker_monitor = DockerMonitor(self.server_ip)
        self.api_monitor = APIHealthMonitor()
        self.db_monitor = DatabaseHealthMonitor()

        self.last_checked = None
        self.data = {}
        self.stop_event = Event()

        self.monitoring_thread = Thread(target=self.background_monitoring, daemon=True)
        self.monitoring_thread.start()

    def background_monitoring(self):
        while not self.stop_event.is_set():
            try:
                self.monitor_all()
            except Exception as e:
                print(f"Error during background monitoring: {e}")
            sleep(REFRESH_TIME)

    def monitor_all(self):
        self.last_checked = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        containers = self.docker_monitor.monitor()
        container_alerts = []
        for container in containers:
            container["status_emoji"] = "✅" if container.get("cpu_percentage", 0) <= CPU_THRESHOLD and container.get(
                "memory_percentage", 0
            ) <= RAM_THRESHOLD else "❌"

            if container["status_emoji"] == "❌":
                container_alerts.append(
                    f"Container {container['name']} has high resource usage: CPU {container.get('cpu_percentage', 'N/A')}%, Memory {container.get('memory_percentage', 'N/A')}%."
                )

        apis = self.api_monitor.monitor(self.openweathermap_api_key)
        api_alerts = []
        for api_name, status in apis.items():
            if not status:
                api_alerts.append(f"API {api_name} is unreachable.")

        databases = self.db_monitor.monitor(
            self.mysql_config, self.influxdb_host, self.influxdb_port
        )
        db_alerts = []
        for db_name, status in databases.items():
            if not status:
                db_alerts.append(f"Database {db_name} is unreachable.")

        self.data = {"containers": containers, "apis": apis, "databases": databases}
        all_alerts = container_alerts + api_alerts + db_alerts
        if all_alerts:
            self.publish_alerts(all_alerts)

    def publish_alerts(self, alerts):
        message = {"Alerts": alerts}
        try:
            self.mqtt_client.publish(self.mqtt_topic, json.dumps(message))
            print(f"Published MQTT alerts: {alerts}")
        except Exception as e:
            print(f"Error publishing MQTT alerts: {e}")

    def render_html(self):
        """Render HTML using a template file."""
        with open("plain_text.html", "r") as file:
            html_template = file.read()

Davood Shaterzadeh, [11/21/2024 7:32 PM]
containers_html = ""
        for container in self.data.get("containers", []):
            name = container["name"]
            state = container.get("state", "Unknown")
            status = container.get("status", "Unknown")
            cpu_usage = container.get("cpu_percentage", "N/A")
            memory_usage = container.get("memory_percentage", "N/A")
            health = container.get("status_emoji", "❌")

            containers_html += f"""
                <tr>
                    <td>{name}</td>
                    <td>{state}</td>
                    <td>{status}</td>
                    <td>{cpu_usage}</td>
                    <td>{memory_usage}</td>
                    <td class="{ 'healthy' if health == '✅' else 'unhealthy' }">{health}</td>
                </tr>"""

        apis_html = "".join(
            f"""
                <tr>
                    <td>{api_name}</td>
                    <td class="{ 'healthy' if health == '✅' else 'unhealthy' }">{health}</td>
                </tr>"""
            for api_name, health in self.data.get("apis", {}).items()
        )

        databases_html = "".join(
            f"""
                <tr>
                    <td>{db_name}</td>
                    <td class="{ 'healthy' if health == '✅' else 'unhealthy' }">{health}</td>
                </tr>"""
            for db_name, health in self.data.get("databases", {}).items()
        )

        #Placeholders for HTML
        html_output = html_template.replace("{{ last_checked }}", self.last_checked)
        html_output = html_output.replace("{{ containers }}", containers_html)
        html_output = html_output.replace("{{ apis }}", apis_html)
        html_output = html_output.replace("{{ databases }}", databases_html)

        return html_output

    @cherrypy.expose
    def index(self):
        """Render the monitoring page."""
        return self.render_html()

    def stop(self):
        """Stop the background thread."""
        self.stop_event.set()
        self.mqtt_client.loop_stop()


if name == "__main__":
    app = IoTMonitoringWebApp()
    try:
        cherrypy.quickstart(app, "/", {
            'global': {
                'server.socket_host': SERVER_HOST,
                'server.socket_port': SERVER_PORT,
            }
        })
    finally:
        app.stop()