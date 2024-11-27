import time
import subprocess

from anyio import sleep

import constants.const as const
from mysqptest import Logic, Delegate


#MYSQL
delegate = Delegate()
logic = Logic(delegate)

CHECK_INTERVAL = const.CHECK_INTERVAL
RUNNING_CHECK_INTERVAL = const.RUNNING_CHECK_INTERVAL

processes = {}


def fetch_area_soil_map():
    # Fetch area list from MySQL
    response = logic.list(params={})

    if response['code'] == 0:
        area_soil_map = {area['name']: area['soil_type'].capitalize() for area in response['list']}
        return area_soil_map
    else:
        print("Error fetching area data:", response['message'])
        return {}


while True:
    # check for updated area
    area_soil_map = fetch_area_soil_map()

    for area, soil_type in area_soil_map.items():
        # Check if there's an active process for this area
        if area in processes:
            if processes[area].poll() is None:
                # Process is still running; skip starting a new one
                time.sleep(RUNNING_CHECK_INTERVAL)
                continue
            else:
                # If the process has finished, remove it from the tracking dictionary
                processes.pop(area)

        # New process starts as the last one is done
        process = subprocess.Popen(['python', 'watering_decision.py', area, soil_type])
        time.sleep(10)
        processes[area] = process

    time.sleep(CHECK_INTERVAL)
