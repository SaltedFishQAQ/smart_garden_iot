import constants.http as const_h
from http import HTTPMethod
from common.time import time_to_str


class Logic:
    def __init__(self, delegate):
        self.delegate = delegate

    def register_handler(self):
        self.delegate.http_client.add_route(const_h.MYSQL_SCHEDULE_LIST, HTTPMethod.GET, self.list)
        self.delegate.http_client.add_route(const_h.MYSQL_SCHEDULE_SAVE, HTTPMethod.POST, self.save)
        self.delegate.http_client.add_route(const_h.MYSQL_SCHEDULE_RUNNING, HTTPMethod.POST, self.running)

    def list(self, params):
        sql = "select * from schedule where 1=1"

        if 'page' in params and 'size' in params:
            page = int(params['page'])
            size = int(params['size'])
            offset = (page - 1) * size
            sql += f" limit {offset}, {size}"

        if 'is_deleted' in params:
            sql += f' and is_deleted = {int(params["is_deleted"])}'

        records = self.delegate.db_connect.query(sql)
        for i in range(len(records)):
            records[i]['created_at'] = time_to_str(records[i]['created_at'])
            records[i]['updated_at'] = time_to_str(records[i]['updated_at'])

        return {
            'list': records
        }

    def save(self, params):
        is_create = False
        if 'id' not in params:
            sql = ('INSERT INTO schedule (target, opt, duration, is_deleted)'
                   'VALUES (%s, %s, %s, %s)')
            args = (params['target'], params['opt'], params['duration'], 0)
            is_create = True
        else:
            sql = ('update schedule set target=%s, opt=%s, `duration`=%s'
                   ' where id=%s')
            args = (params['target'], params['opt'], params['duration'], params['id'])
        n = self.delegate.db_connect.insert(sql, args, is_create=is_create)
        return {
            "row": n
        }

    def running(self, params):
        if params['status'] == 0:
            is_deleted = 1
        else:
            is_deleted = 0
        sql = 'update schedule set is_deleted = %s where id = %s'
        self.delegate.db_connect.insert(sql, (is_deleted, params['id']))
