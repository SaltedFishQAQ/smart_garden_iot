import constants.http as const_h
from http import HTTPMethod
from common.time import time_to_str


class Logic:
    def __init__(self, delegate):
        self.delegate = delegate

    def register_handler(self):
        self.delegate.http_client.add_route(const_h.MYSQL_USER_LIST, HTTPMethod.GET, self.list)
        self.delegate.http_client.add_route(const_h.MYSQL_USER_LOGIN, HTTPMethod.POST, self.login)

    def list(self, params):
        records = self.delegate.db_connect.query("select * from user")
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

    def login(self, params):
        if 'name' not in params or 'password' not in params:
            return "params not found"

        sql = 'select * from user where name = %s and password = %s'
        records = self.delegate.db_connect.query(sql, (params['name'], params['password']))
        if len(records) == 0:
            return "user or password error"

        return {
            "id": records[0]['id'],
            "name": records[0]['name'],
            "role": records[0]['role'],
            "created_at": time_to_str(records[0]['created_at']),
            "updated_at": time_to_str(records[0]['updated_at'])
        }
