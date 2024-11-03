import time
from service.decision.decision_service import DecisionService

if __name__ == '__main__':
    s = DecisionService()
    s.start()
    s.register_controller()

    try:
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        s.stop()