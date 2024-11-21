import requests
import mysql.connector
from mysql.connector import Error
from constant_values import (OPENWEATHERMAP_API,
    OPENMETEO_API, SAMPLE_LONG, SAMPLE_LAT, SAMPLE_CITY)

class DockerMonitor:
    def __init__(self, server_ip):
        self.server_ip = server_ip

    def get_containers(self):
        """Fetch the list of all containers."""
        url = f"http://{self.server_ip}:2375/containers/json"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    def get_container_stats(self, container_id):
        """Fetch CPU and memory stats for a specific container."""
        url = f"http://{self.server_ip}:2375/containers/{container_id}/stats?stream=false"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    def calculate_usage(self, stats):
        """Calculate CPU and memory usage from container stats."""
        total_usage = stats["cpu_stats"]["cpu_usage"]["total_usage"]
        prev_total_usage = stats["precpu_stats"]["cpu_usage"]["total_usage"]
        system_cpu_usage = stats["cpu_stats"]["system_cpu_usage"]
        prev_system_cpu_usage = stats["precpu_stats"]["system_cpu_usage"]
        online_cpus = stats["cpu_stats"].get("online_cpus", 1)

        cpu_delta = total_usage - prev_total_usage
        system_delta = system_cpu_usage - prev_system_cpu_usage

        cpu_percentage = (cpu_delta / system_delta) * online_cpus * 100 if system_delta > 0 else 0

        memory_usage = stats["memory_stats"]["usage"]
        memory_limit = stats["memory_stats"]["limit"]
        memory_percentage = (memory_usage / memory_limit) * 100 if memory_limit > 0 else 0

        return {
            "cpu_percentage": round(cpu_percentage, 2),
            "memory_usage_mb": round(memory_usage / (1024 * 1024), 2),
            "memory_percentage": round(memory_percentage, 2),
        }

    def monitor(self):
        """Monitor all containers and return stats."""
        containers = self.get_containers()
        container_stats = []

        for container in containers:
            container_id = container["Id"]
            container_name = container["Names"][0] if container["Names"] else "Unknown"
            container_state = container["State"]
            container_status = container["Status"]

            stats_data = {
                "name": container_name,
                "state": container_state,
                "status": container_status,
            }

            try:
                stats = self.get_container_stats(container_id)
                usage = self.calculate_usage(stats)
                stats_data.update(usage)
            except Exception as e:
                stats_data["error"] = f"Failed to fetch stats: {e}"

            container_stats.append(stats_data)

        return container_stats


class APIHealthMonitor:
    @staticmethod
    def check_openweathermap(api_key):
        url = OPENWEATHERMAP_API
        params = {"q": SAMPLE_CITY, "appid": api_key}
        try:
            response = requests.get(url, params=params)
            return response.status_code == 200
        except Exception:
            return False

    @staticmethod
    def check_open_meteo():
        url = OPENMETEO_API
        params = {"latitude": SAMPLE_LAT, "longitude": SAMPLE_LONG, "current_weather": "true"}
        try:
            response = requests.get(url, params=params)
            return response.status_code == 200
        except Exception:
            return False

    def monitor(self, api_key):
        return {
            "openweathermap": self.check_openweathermap(api_key),
            "open_meteo": self.check_open_meteo(),
        }

class DatabaseHealthMonitor:
    @staticmethod
    def check_mysql(config):
        try:
            connection = mysql.connector.connect(
                host=config["host"],
                port=config["port"],
                user=config["user"],
                password=config["password"],
                database=config["database"],
            )
            if connection.is_connected():
                cursor = connection.cursor()
                cursor.execute("SELECT 1;")
                result = cursor.fetchone()
                cursor.close()
                connection.close()
                return result is not None
        except Error:
            return False

    @staticmethod
    def check_influxdb(host, port):
        url = f"http://{host}:{port}/health"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                health = response.json()
                return health.get("status") == "pass"
            return False
        except Exception:
            return False

    def monitor(self, mysql_config, influxdb_host, influxdb_port):
        return {
            "mysql": self.check_mysql(mysql_config),
            "influxdb": self.check_influxdb(influxdb_host, influxdb_port),
        }