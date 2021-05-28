from db import fast_db
from .base import AppService


class RequestService(AppService):

    def __init__(self):
        super(RequestService, self).__init__()
        self.request_limit = self.app_config.get('REQUEST_LIMIT')

    def check_user_limit(self, user_id):
        return fast_db.get_user_request_count(user_id) < self.request_limit
