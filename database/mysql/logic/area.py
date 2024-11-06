import constants.http as const_h
from http import HTTPMethod


class Logic:
    def __init__(self, delegate):
        self.delegate = delegate

    def register_handler(self):
        self.delegate.http_client.add_route(const_h.MYSQL_AREA_LIST, HTTPMethod.GET, self.list)
        self.delegate.http_client.add_route(const_h.MYSQL_AREA_SAVE, HTTPMethod.POST, self.save)

    def list(self, params):
        records = self.delegate.db_connect.query("select * from area")
        result = []
        for record in records:
            result.append({
                'id': record['id'],
                'name': record['name'],
                'user_id': record['user_id'],
                'soil_type': record['soil_type'],
                'desc': record['desc'],
            })

        return {
            'list': result
        }

    def save(self, params):
        is_create = False
        if 'id' not in params:
            sql = ('INSERT INTO area (name, user_id, soil_type, `desc`)'
                   'VALUES (%s, %s, %s, %s)')
            args = (params['name'], params['user_id'], params['soil_type'], params['desc'])
            is_create = True
        else:
            sql = ('update area set name=%s, user_id=%s, soil_type=%s, `desc`=%s'
                   ' where id=%s')
            args = (params['name'], params['user_id'], params['soil_type'], params['desc'], params['id'])
        n = self.delegate.db_connect.insert(sql, args, is_create=is_create)
        return {
            "row": n
        }