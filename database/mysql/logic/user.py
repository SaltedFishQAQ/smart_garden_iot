import constants.http as const_h
from http import HTTPMethod
from common.time import time_to_str


class Logic:
    def __init__(self, delegate):
        self.delegate = delegate

    def register_handler(self):
        self.delegate.http_client.add_route(const_h.MYSQL_USER_LIST, HTTPMethod.GET, self.list)
        self.delegate.http_client.add_route(const_h.MYSQL_USER_LOGIN, HTTPMethod.POST, self.login)
        self.delegate.http_client.add_route(const_h.MYSQL_USER_REGISTER, HTTPMethod.POST, self.register)

    def list(self, params):
        sql = "select * from user"
        if 'id' in params:
            sql += f' where id = {params["id"]}'

        records = self.delegate.db_connect.query(sql)
        result = []
        for record in records:
            result.append({
                'id': record['id'],
                'name': record['name'],
                'role': record['role'],
                'created_at': time_to_str(record['created_at']),
                'updated_at': time_to_str(record['updated_at'])
            })

        return {
            'list': result
        }

    def find_by_name(self, name):
        if name == "":
            return {}, "params invalid"

        sql = 'select * from user where name = %s'
        records = self.delegate.db_connect.query(sql, name)
        if len(records) == 0:
            return {}, "record not found"

        return records[0], ""

    def login(self, params):
        if 'name' not in params or 'password' not in params:
            return "params not found"

        user, err = self.find_by_name(params['name'])
        if err != "":
            return err

        if user['password'] != params['password']:
            return "password not match"

        return {
            "id": user['id'],
            "name": user['name'],
            "role": user['role'],
            "created_at": time_to_str(user['created_at']),
            "updated_at": time_to_str(user['updated_at'])
        }

    def register(self, params):
        if 'name' not in params or 'password' not in params:
            return "params invalid"

        user, err = self.find_by_name(params['name'])
        if err == "":
            return "user already exists"

        if err != "record not found":
            return err

        sql = ('INSERT INTO user (name, password, role)'
               'VALUES (%s, %s, %s)')
        args = (params['name'], params['password'], 2)
        self.delegate.db_connect.insert(sql, args)
