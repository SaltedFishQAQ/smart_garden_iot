import constants.http as const_h
from http import HTTPMethod
from common.time import time_to_str


class Logic:
    def __init__(self, delegate):
        self.delegate = delegate

    def register_handler(self):
        self.delegate.http_client.add_route(const_h.MYSQL_DEVICE_LIST, HTTPMethod.GET, self.list)
        self.delegate.http_client.add_route(const_h.MYSQL_DEVICE_COUNT, HTTPMethod.GET, self.count)
        self.delegate.http_client.add_route(const_h.MYSQL_DEVICE_CERTIFIED_LIST, HTTPMethod.GET, self.certified_list)
        self.delegate.http_client.add_route(const_h.MYSQL_DEVICE_REGISTER, HTTPMethod.POST, self.register)
        self.delegate.http_client.add_route(const_h.MYSQL_DEVICE_APPROVE, HTTPMethod.POST, self.approve)

    def count(self, params):
        records = self.delegate.db_connect.query("select count(*) as total from device")
        count = 0
        for record in records:
            count += record['total']

        return {
            'count': count
        }

    def list(self, params):
        records = self.delegate.db_connect.query("select * from device")
        result = []
        for record in records:
            result.append({
                'id': record['id'],
                'name': record['name'],
                'running_status': record['running_status'],
                'auth_status': record['auth_status'],
                'created_at': time_to_str(record['created_at']),
                'updated_at': time_to_str(record['updated_at'])
            })

        return {
            'list': result
        }

    def certified_list(self, params):
        records = self.delegate.db_connect.query("select id, name from device where auth_status = 1")
        result = []
        for record in records:
            result.append({
                'id': record['id'],
                'name': record['name']
            })

        return {
            'list': result
        }

    def register(self, params):
        name = params['name']
        area_name = params['area']
        status = params['status']

        area_id = 0
        records = self.delegate.db_connect.query('select id from area where name = %s limit 1', area_name)
        if len(records) > 0:
            for record in records:
                area_id = record['id']

        select = 'select id from device where name = %s limit 1'
        records = self.delegate.db_connect.query(select, name)

        is_create = False
        if len(records) == 0:
            sql = ('INSERT INTO device (name, running_status, auth_status, area_id)'
                   'VALUES (%s, %s, %s, %s)')
            args = (name, status, 0, area_id)
            is_create = True
        else:
            sql = 'update device set running_status = %s, area_id = %s where name = %s'
            args = (status, area_id, name)

        self.delegate.db_connect.insert(sql, args, is_create=is_create)

    def approve(self, params):
        name = params['name']
        status = params['status']

        select = 'select id from device where name = %s limit 1'
        records = self.delegate.db_connect.query(select, name)

        if len(records) == 0:
            return {
                'code': 400,
                'message': 'record not found'
            }

        sql = 'update device set auth_status = %s where name = %s'
        args = (status, name)
        self.delegate.db_connect.insert(sql, args)

        return {
            'code': 0,
            'message': 'success'
        }
