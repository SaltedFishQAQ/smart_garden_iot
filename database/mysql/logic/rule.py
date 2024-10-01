import constants.http as const_h
from http import HTTPMethod
from common.time import time_to_str


class Logic:
    def __init__(self, delegate):
        self.delegate = delegate

    def register_handler(self):
        self.delegate.http_client.add_route(const_h.MYSQL_RULE_LIST, HTTPMethod.GET, self.list)
        self.delegate.http_client.add_route(const_h.MYSQL_RULE_COUNT, HTTPMethod.GET, self.list)
        self.delegate.http_client.add_route(const_h.MYSQL_RULE_SAVE, HTTPMethod.POST, self.save)
        self.delegate.http_client.add_route(const_h.MYSQL_RULE_RUNNING, HTTPMethod.POST, self.running)

    def count(self, params):
        records = self.delegate.db_connect.query("select count(*) as total from rule")
        count = 0
        for record in records:
            count += record['total']

        return {
            'count': count
        }

    def list(self, params):
        sql = "select * from rule where 1=1"

        if 'is_deleted' in params:
            sql += f' and is_deleted = {int(params["is_deleted"])}'

        if 'name' in params and params['name'] != "":
            sql += f" and src = {params['name']}"

        if 'page' in params and 'size' in params:
            page = int(params['page'])
            size = int(params['size'])
            offset = (page-1) * size
            sql += f" limit {offset}, {size}"

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
            sql = ('INSERT INTO rule (src, entity, `field`, compare, value, dst, opt, is_deleted, `desc`)'
                   'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)')
            args = (params['src'], params['entity'], params['field'],
                    params['compare'], params['value'], params['dst'],
                    params['opt'], 0, params['desc'])
            is_create = True
        else:
            sql = ('update rule set src=%s, entity=%s, `field`=%s, compare=%s, value=%s, dst=%s, opt=%s, `desc`=%s'
                   ' where id=%s')
            args = (params['src'], params['entity'], params['field'],
                    params['compare'], params['value'], params['dst'],
                    params['opt'], params['desc'], params['id'])
        n = self.delegate.db_connect.insert(sql, args, is_create=is_create)
        return {
            "row": n
        }

    def running(self, params):
        if params['status'] == 0:
            is_deleted = 1
        else:
            is_deleted = 0
        sql = 'update rule set is_deleted = %s where id = %s'
        self.delegate.db_connect.insert(sql, (is_deleted, params['id']))
