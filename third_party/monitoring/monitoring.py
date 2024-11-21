import requests
import mysql.connector
from mysql.connector import Error

# Container Monitoring
def get_containers(server_ip):
    """Fetch the list of all containers."""
    url = f"http://{server_ip}:2375/containers/json"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def get_container_stats(server_ip, container_id):
    """Fetch CPU and memory stats for a specific container."""
    url = f"http://{server_ip}:2375/containers/{container_id}/stats?stream=false"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def calculate_usage(stats):
    """Calculate CPU and memory usage from container stats."""
    # CPU Calculation
    total_usage = stats["cpu_stats"]["cpu_usage"]["total_usage"]
    prev_total_usage = stats["precpu_stats"]["cpu_usage"]["total_usage"]
    system_cpu_usage = stats["cpu_stats"]["system_cpu_usage"]
    prev_system_cpu_usage = stats["precpu_stats"]["system_cpu_usage"]
    online_cpus = stats["cpu_stats"].get("online_cpus", 1)

    cpu_delta = total_usage - prev_total_usage
    system_delta = system_cpu_usage - prev_system_cpu_usage

    cpu_percentage = (cpu_delta / system_delta) * online_cpus * 100 if system_delta > 0 else 0

    # Memory Calculation
    memory_usage = stats["memory_stats"]["usage"]
    memory_limit = stats["memory_stats"]["limit"]
    memory_percentage = (memory_usage / memory_limit) * 100 if memory_limit > 0 else 0

    return {
        "cpu_percentage": round(cpu_percentage, 2),
        "memory_usage_mb": round(memory_usage / (1024 * 1024), 2),
        "memory_percentage": round(memory_percentage, 2)
    }

def monitor_containers(server_ip):
    """Monitor all containers and print their stats."""
    print("Checking Docker containers...")
    containers = get_containers(server_ip)

    for container in containers:
        container_id = container["Id"]
        container_name = container["Names"][0] if container["Names"] else "Unknown"
        container_state = container["State"]
        container_status = container["Status"]

        print(f"Container: {container_name}")
        print(f"  State: {container_state}")
        print(f"  Status: {container_status}")

        try:
            stats = get_container_stats(server_ip, container_id)
            usage = calculate_usage(stats)
            print(f"  CPU Usage: {usage['cpu_percentage']}%")
            print(f"  Memory Usage: {usage['memory_usage_mb']} MB ({usage['memory_percentage']}%)")
        except Exception as e:
            print(f"  Failed to fetch stats: {e}")

        print("-" * 40)

# API Health Checks
def check_openweathermap(api_key):
    """Check OpenWeatherMap API health."""
    print("Checking OpenWeatherMap API...")
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"q": "London", "appid": api_key}
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            print("OpenWeatherMap API is up and reachable.")
        else:
            print(f"OpenWeatherMap API returned status code: {response.status_code}")
    except Exception as e:
        print(f"Error connecting to OpenWeatherMap API: {e}")

def check_open_meteo():
    """Check Open-Meteo API health."""
    print("Checking Open-Meteo API...")
    url = "https://api.open-meteo.com/v1/forecast"
    params = {"latitude": 51.5074, "longitude": -0.1278, "current_weather": "true"}
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            print("Open-Meteo API is up and reachable.")
        else:
            print(f"Open-Meteo API returned status code: {response.status_code}")
    except Exception as e:
        print(f"Error connecting to Open-Meteo API: {e}")

def monitor_apis(api_key):
    """Monitor API health."""
    print("Checking API health...")
    check_openweathermap(api_key)
    check_open_meteo()
    print("-" * 40)

# Database Health Checks
def check_mysql(host, port, user, password, database):
    """Check MySQL availability by connecting and running a simple query."""
    print("Checking MySQL...")
    try:
        connection = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database
        )
        if connection.is_connected():
            cursor = connection.cursor()
            cursor.execute("SELECT 1;")
            result = cursor.fetchone()
            if result:
                print("MySQL is up and reachable.")
            cursor.close()
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
    finally:
        if connection.is_connected():
            connection.close()

def check_influxdb(host, port):
    """Check InfluxDB availability using the /health endpoint."""
    print("Checking InfluxDB...")
    url = f"http://{host}:{port}/health"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            health = response.json()
            if health.get("status") == "pass":
                print("InfluxDB is up and reachable.")
            else:
                print("InfluxDB is reachable but reports an issue.")
        else:
            print(f"InfluxDB returned status code: {response.status_code}")
    except Exception as e:
        print(f"Error connecting to InfluxDB: {e}")

def monitor_databases(mysql_config, influxdb_host, influxdb_port):
    """Monitor database health."""
    print("Checking database health...")
    check_mysql(**mysql_config)
    check_influxdb(influxdb_host, influxdb_port)
    print("-" * 40)

# Configuration
server_ip = "43.131.48.203"
openweathermap_api_key = "5dc8ece6e02d649d870e2e3a67ffc128"
mysql_config = {
    "host": "43.131.48.203",
    "port": 3306,
    "user": "iot",
    "password": "Test1234.",
    "database": "iot_test"
}
influxdb_host = "43.131.48.203"
influxdb_port = 18086

# Run monitoring
monitor_containers(server_ip)
monitor_apis(openweathermap_api_key)
monitor_databases(mysql_config, influxdb_host, influxdb_port)