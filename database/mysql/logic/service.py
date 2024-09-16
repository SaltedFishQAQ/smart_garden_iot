import constants.http as const_h
from http import HTTPMethod
from common.time import time_to_str, time_add
from datetime import datetime


class Logic:
    def __init__(self, delegate):
        self.delegate = delegate

    def register_handler(self):
        self.delegate.http_client.add_route(const_h.MYSQL_SERVICE_LIST, HTTPMethod.GET, self.list)
        self.delegate.http_client.add_route(const_h.MYSQL_SERVICE_REGISTER, HTTPMethod.POST, self.register)

    def list(self, params):
        records = self.delegate.db_connect.query("select * from service")
        result = []
        for record in records:
            running = 1
            if record['last_running'] is None or record['last_running'] < time_add(datetime.now(), -30 * 60):
                running = 0

            if record['name'] == self.delegate.service_name:
                running = 1

            result.append({
                'id': records[0]['id'],
                'name': records[0]['name'],
                'desc': records[0]['desc'],
                'running': running,
                'created_at': time_to_str(record['created_at']),
                'updated_at': time_to_str(record['updated_at'])
            })

        return {
            'list': result
        }

    def register(self, params):
        name = params['name']

        select = 'select id from service where name = %s limit 1'
        records = self.delegate.db_connect.query(select, name)

        is_create = False
        if len(records) == 0:
            sql = ('INSERT INTO service (name, `desc`, last_running) '
                   'VALUES (%s, %s, %s)')
            args = (name, '', datetime.now())
            is_create = True
        else:
            sql = 'update service set last_running = %s where name = %s'
            args = (datetime.now(), name)
        self.delegate.db_connect.insert(sql, args, is_create=is_create)
