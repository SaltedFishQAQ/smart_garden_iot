import constants.entity
from common.base_service import BaseService


class UserService(BaseService):
    def __init__(self):
        super().__init__(constants.entity.USER_SERVICE)

