import cherrypy
from datetime import datetime
from threading import Thread, Event
from time import sleep
from monitoring import DockerMonitor, APIHealthMonitor, DatabaseHealthMonitor
import paho.mqtt.client as mqtt
import json
from pytz import timezone
from constant_values import (
    IP_SERVER,
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
        self.server_ip = IP_SERVER
        self.openweathermap_api_key = OPENWEATHERMAP_API_KEY
        self.mysql_config = MYSQL_CONFIG
        self.influxdb_host = INFLUXDB_HOST
        self.influxdb_port = INFLUXDB_PORT

        self.mqtt_broker = MQTT_BROKER
        self.mqtt_port = MQTT_PORT
        self.mqtt_topic = MQTT_TOPIC        #pull constants from constant_values.py to configure server communication, database access, and API requests
        self.mqtt_client = mqtt.Client()    #publish system alerts to MQTT broker

        try:
            self.mqtt_client.connect(self.mqtt_broker, self.mqtt_port)
            self.mqtt_client.loop_start()
            print(f"Connected to MQTT broker at {self.mqtt_broker}:{self.mqtt_port}")
        except Exception as e:
            print(f"Error connecting to MQTT broker: {e}")

        self.docker_monitor = DockerMonitor(self.server_ip)
        self.api_monitor = APIHealthMonitor()
        self.db_monitor = DatabaseHealthMonitor()     #handle Docker container health, API availability, and database status checks

        self.last_checked = None
        self.data = {"containers": [], "apis": {}, "databases": {}}
        self.stop_event = Event()

        self.monitoring_thread = Thread(target=self.background_monitoring, daemon=True)
        self.monitoring_thread.start()

    def background_monitoring(self):    #Runs in a background thread to continuously monitor all system components
        while not self.stop_event.is_set():
            try:
                self.monitor_all()
            except Exception as e:
                print(f"Error during background monitoring: {e}")
            sleep(REFRESH_TIME)

    def monitor_all(self):      #Collects the status of containers, APIs, and databases
        localzone = timezone('Europe/Rome')
        self.last_checked = datetime.now(localzone).strftime("%Y-%m-%d %H:%M:%S")

        # Monitor containers
        containers, events = self.docker_monitor.monitor()
        for event in events:
            self.publish_alerts([event])

        # Monitor APIs
        apis = self.api_monitor.monitor(self.openweathermap_api_key)
        self.data["apis"] = apis

        # Monitor databases
        databases = self.db_monitor.monitor(self.mysql_config, self.influxdb_host, self.influxdb_port)
        self.data["databases"] = databases

        # Update data
        self.data["containers"] = containers

    def publish_alerts(self, alerts):
        """Send alerts to the MQTT broker."""
        message = {"Alerts": alerts}
        try:
            self.mqtt_client.publish(self.mqtt_topic, json.dumps(message))
            print(f"Published MQTT alerts: {alerts}")
        except Exception as e:
            print(f"Error publishing MQTT alerts: {e}")

    def render_html(self):
        """Render HTML dashboard with current data."""
        with open("plain_text.html", "r") as file:
            html_template = file.read()

        containers_html = ""
        for container in self.data["containers"]:
            name = container["name"]
            state = container.get("state", "Unknown")
            status = container.get("status", "Unknown")
            cpu_usage = container.get("cpu_percentage", "N/A")
            memory_usage = container.get("memory_percentage", "N/A")
            health = "✅" if cpu_usage != "N/A" and memory_usage != "N/A" and \
                           cpu_usage <= CPU_THRESHOLD and memory_usage <= RAM_THRESHOLD else "❌"

            containers_html += f"""
                <tr>
                    <td>{name}</td>
                    <td>{state}</td>
                    <td>{status}</td>
                    <td>{cpu_usage}</td>
                    <td>{memory_usage}</td>
                    <td>{health}</td>
                </tr>"""

        # Render APIs
        apis_html = "".join(
            f"""
                <tr>
                    <td>{api_name}</td>
                    <td>{'✅' if health else '❌'}</td>
                </tr>"""
            for api_name, health in self.data.get("apis", {}).items()
        )

        # Render Databases
        databases_html = "".join(
            f"""
                <tr>
                    <td>{db_name}</td>
                    <td>{'✅' if health else '❌'}</td>
                </tr>"""
            for db_name, health in self.data.get("databases", {}).items()
        )

        html_output = html_template.replace("{{ last_checked }}", self.last_checked or "N/A")
        html_output = html_output.replace("{{ containers }}", containers_html)
        html_output = html_output.replace("{{ apis }}", apis_html)
        html_output = html_output.replace("{{ databases }}", databases_html)

        return html_output

    @cherrypy.expose
    def index(self):
        """Serve the monitoring dashboard."""
        return self.render_html()  #Renders the monitoring dashboard in the browser

    def stop(self):
        """Stop the monitoring thread and MQTT client."""
        self.stop_event.set()
        self.mqtt_client.loop_stop()


if __name__ == "__main__":
    app = IoTMonitoringWebApp()     
    try:
        cherrypy.quickstart(app, "/", {        #launches the application
            'global': {
                'server.socket_host': SERVER_HOST,
                'server.socket_port': SERVER_PORT,
            }
        })
    finally:
        app.stop()


