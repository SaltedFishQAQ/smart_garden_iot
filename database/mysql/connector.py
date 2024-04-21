import pymysql
from dbutils.pooled_db import PooledDB


class Connector:
    def __init__(self, host, port, user, password, db):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.db = db
        self.pool = PooledDB(pymysql,
                             mincached=1,
                             maxcached=20,
                             host=host,
                             port=port,
                             user=user,
                             password=password,
                             database=db,
                             autocommit=True,
                             charset='utf8mb4')

    def insert(self, sql, args):
        connection = self.pool.connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, args)

                return cursor.rowcount
        finally:
            cursor.close()
            connection.close()

    def query(self, sql):
        connection = self.pool.connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql)
                results = cursor.fetchall()

                return results
        finally:
            cursor.close()
            connection.close()
