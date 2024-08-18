import time
from service.auth.auth_service import AuthService


if __name__ == '__main__':
    s = AuthService()
    s.start()
    s.register_mqtt_service()
    try:
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        s.stop()

