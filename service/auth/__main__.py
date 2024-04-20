from service.auth.auth_service import AuthService


if __name__ == '__main__':
    s = AuthService()
    s.start()
    s.register_mqtt_service()

    while True:
        if input("stop running [q]:") == 'q':
            break

    s.stop()

