import datetime
from typing import Optional

from db import fast_db
from db.db_models import User as db_User
from .base import AppService


class SessionService(AppService):

    def __init__(self):
        super(SessionService, self).__init__()
        self.session_expiration = self.app_config.get("SESSION_EXPIRATION")

    def create_session(self, db_user: db_User):
        session_id = fast_db.add_user_session(db_user.id, self.session_expiration)
        return session_id, expiration_from_now(self.session_expiration)

    def check_session_id(self, session_id) -> Optional[str]:
        return fast_db.get_session_data(session_id)


def expiration_from_now(expiration_in_seconds: int):
    expires = datetime.datetime.now() + datetime.timedelta(seconds=expiration_in_seconds)
    return expires.strftime('%a, %d %b %Y %H:%M:%S GMT')
