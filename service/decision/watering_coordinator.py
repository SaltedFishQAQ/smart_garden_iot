import time
import subprocess
import constants.const as const

# Define the dictionary of areas and their soil types
area_soil_map = {
    'area1': 'Clay',
    'area2': 'Sandy',
    'area3': 'Loamy',
    'area4': 'Silty'
}

# Define the interval (5 minutes in seconds)
CHECK_INTERVAL = const.CHECK_INTERVAL
RUNNING_CHECK_INTERVAL = const.RUNNING_CHECK_INTERVAL

# Dictionary to track running processes for each area
processes = {}

while True:
    for area, soil_type in area_soil_map.items():
        # Check if there's an active process for this area
        if area in processes:
            if processes[area].poll() is None:
                ##print(f"Process for {area} is still running. Skipping new command.")
                time.sleep(RUNNING_CHECK_INTERVAL)
                continue
            else:
                # If the process has finished, we can remove it from the tracking dictionary
                ##print(f"Process for {area} has finished.")
                processes.pop(area)

        # Start a new process for the area if no active process exists
        ##print(f"Sending request to watering_decision.py for {area} with soil type {soil_type}")
        process = subprocess.Popen(['python', 'watering_decision.py', area, soil_type])
        processes[area] = process  # Store the process in the dictionary


    # Wait for the specified interval before the next check
        ##print(f"Sleeping for {CHECK_INTERVAL / 60} minutes before the next check...")
        time.sleep(CHECK_INTERVAL)
