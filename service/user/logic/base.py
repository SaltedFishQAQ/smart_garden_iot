import requests
import constants.http as const_h


class Common:
    def __init__(self, delegate):
        self.delegate = delegate
        self.mysql_base_url = f'{const_h.MYSQL_HOST}:{const_h.SERVICE_PORT_MYSQL}'

    @staticmethod
    def check_params(params, keys):
        for key in keys:
            if key not in params:
                return {
                    'code': 500,
                    'message': f'params not found: {key}'
                }
        return None

    def get_user(self, params):
        if 'user_id' not in params:
            return None
        resp = requests.get(self.mysql_base_url + const_h.MYSQL_USER_LIST, {
            'id': params['user_id']
        })
        user_list = resp.json()['list']
        if len(user_list) == 0:
            return None

        return user_list[0]

    def get_area_list(self, params):
        if 'user_id' not in params:
            return []
        resp = requests.get(self.mysql_base_url + const_h.MYSQL_AREA_LIST, params)
        return resp.json()['list']

    def get_area_ids(self, params):
        area_list = self.get_area_list(params)
        if len(area_list) == 0:
            return []
        return [item['id'] for item in area_list]
