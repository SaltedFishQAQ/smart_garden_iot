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

    def get_user(self):
        return self.delegate.http_client.get_user()

    def get_area_list(self, params):
        user = self.get_user()
        if user is None:
            return [0]
        if user['role'] != 1:
            params['user_id'] = user['id']
        resp = requests.get(self.mysql_base_url + const_h.MYSQL_AREA_LIST, params)
        return resp.json()['list']

    def get_area_ids(self, params):
        area_list = self.get_area_list(params)
        if len(area_list) == 0:
            return []
        return [item['id'] for item in area_list]
