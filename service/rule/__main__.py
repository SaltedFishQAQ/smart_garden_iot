import time
from service.rule.rule_service import RuleService

if __name__ == '__main__':
    s = RuleService()
    s.start()
    s.register_mqtt_service()

    try:
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        s.stop()
