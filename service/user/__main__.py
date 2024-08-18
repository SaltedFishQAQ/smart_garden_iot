import time
from service.user.user_service import UserService

if __name__ == '__main__':
    s = UserService()
    s.start()
    s.register_http_service()

    try:
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        s.stop()
