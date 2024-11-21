import requests

def get_containers(server_ip):
    """Fetch the list of all containers."""
    url = f"http://{server_ip}:2375/containers/json"
    response = requests.get(url)
    response.raise_for_status()  # Raise an error for bad HTTP responses
    return response.json()

def get_container_stats(server_ip, container_id):
    """Fetch CPU and memory stats for a specific container."""
    url = f"http://{server_ip}:2375/containers/{container_id}/stats?stream=false"
    response = requests.get(url)
    response.raise_for_status()  # Raise an error for bad HTTP responses
    return response.json()

def calculate_usage(stats):
    """Calculate CPU and memory usage from container stats."""
    # CPU Calculation
    total_usage = stats["cpu_stats"]["cpu_usage"]["total_usage"] #Total_usage status
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

# Replace with your server IP
server_ip = "3.79.189.115"
monitor_containers(server_ip)
