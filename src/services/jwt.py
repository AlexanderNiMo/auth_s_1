import datetime
from uuid import UUID, uuid4

import jwt

from db import fast_db
from .base import AppService


class JWTService(AppService):

    def __init__(self):
        super(JWTService, self).__init__()
        self._secret = self.app_config.get('JWT_SECRET')
        self.jwt_token_expiration = self.app_config.get('JWT_TOKEN_EXPIRATION')

    def generate_jwt_pair(self, user_id: UUID):

        jwt_token = jwt.encode(
            {
                "user_id": str(user_id),
                'exp': datetime.datetime.utcnow() + datetime.timedelta(self.jwt_token_expiration),
                'iat': datetime.datetime.utcnow()
            },
            key=self._secret, algorithm="HS256")
        refresh_token = uuid4()
        fast_db.add_jwt_refresh_token(user_id, refresh_token)

        return {
            'jwt_token': jwt_token,
            'refresh_token': refresh_token,
        }

    def check_jwt(self, jwt_token: str):
        try:
            data = jwt.decode(jwt_token, key=self._secret, algorithms=["HS256"])
            if datetime.datetime.fromtimestamp(data.get('exp')) < datetime.datetime.utcnow():
                return None
        except jwt.DecodeError as ex:
            return None
        return data

    def get_jwt_data(self, jwt_token):
        try:
            data = jwt.decode(jwt_token, key=self._secret, algorithms=["HS256"])
        except jwt.DecodeError as ex:
            return None
        return data

    def expire_all_refresh_tokens(self, user_id: UUID):
        fast_db.clear_all_refresh_token(user_id)

    def refresh_jwt(self, user_id: UUID, refresh_token: str):
        if fast_db.check_jwt_refresh_token(user_id, refresh_token):
            return self.generate_jwt_pair(user_id)
        return None
