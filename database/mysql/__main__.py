from database.mysql.mysql_adapter import MysqlAdapter


if __name__ == '__main__':
    m = MysqlAdapter()
    m.start()
    m.register_http_service()
    while True:
        if input("stop running [q]:") == 'q':
            break

    m.stop()
