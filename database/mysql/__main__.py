import time
from database.mysql.mysql_adapter import MysqlAdapter


if __name__ == '__main__':
    m = MysqlAdapter()
    m.start()
    m.register_http_service()
    try:
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        m.stop()
