from service.user.user_service import UserService

if __name__ == '__main__':
    s = UserService()
    s.start()
    s.register_http_service()
    while True:
        if input("stop running [q]:") == 'q':
            break

    s.stop()
