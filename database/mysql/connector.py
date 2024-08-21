import pymysql
from dbutils.pooled_db import PooledDB
from pymysql.cursors import DictCursor


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

    def insert(self, sql, args, is_create=False):
        connection = self.pool.connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, args)
            connection.commit()
            if is_create:
                return cursor.lastrowid

            return cursor.rowcount
        finally:
            cursor.close()
            connection.close()

    def query(self, sql, args=None):
        connection = self.pool.connection()
        try:
            with connection.cursor(DictCursor) as cursor:
                cursor.execute(sql, args)
                results = cursor.fetchall()

                return results
        finally:
            cursor.close()
            connection.close()
