import time
from service.schedule.schedule_service import ScheduleService

if __name__ == '__main__':
    s = ScheduleService()
    s.start()

    try:
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        s.stop()
