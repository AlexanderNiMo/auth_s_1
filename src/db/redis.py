from datetime import datetime
from uuid import UUID

import redis

from .base import FastDB


class RedisDB(FastDB):

    def __init__(self, refresh_token_expiration: int, redis_connection: redis.Redis):
        super(RedisDB, self).__init__(refresh_token_expiration=refresh_token_expiration)
        self.redis = redis_connection

    def _session_key(self, session_id: UUID):
        return f'user_session:{session_id}'

    def _refresh_token_key(self, user_id, refresh_token):
        return f'{self._refresh_token_pattern(user_id)}:{refresh_token}'

    def _refresh_token_pattern(self, user_id):
        return f'refresh_token:{user_id}'

    def get_session_data(self, session_id: UUID):
        session_data = self.redis.get(self._session_key(session_id))
        if session_data is None:
            return ''
        session_data = session_data.decode()
        return UUID(session_data)

    def add_user_session(self, user_id: UUID, session_expiration: int):
        session_id = self._gen_session_id()
        self.redis.set(self._session_key(session_id), str(user_id), session_expiration)
        return session_id

    def pop_session(self, session_id):
        self.redis.delete(self._session_key(session_id))

    def add_jwt_refresh_token(self, user_id: UUID, refresh_token: UUID):
        self.redis.set(self._refresh_token_key(user_id, refresh_token), 0, self.refresh_token_expiration)

    def check_jwt_refresh_token(self, user_id, refresh_token):
        data = self.redis.get(self._refresh_token_key(user_id, refresh_token))
        return data == b'0'

    def clear_all_refresh_token(self, user_id: UUID):
        refresh_token_keys = self.redis.keys(
            f'{self._refresh_token_pattern(user_id)}:*'
        )
        if refresh_token_keys:
            self.redis.delete(*refresh_token_keys)

    def _request_key(self, user_id: UUID, now_minute):
        return f'{self._request_key_prefix(user_id)}:{now_minute}'

    def _request_key_prefix(self, user_id: UUID):
        return f'request:{user_id}'

    def get_user_request_count(self, user_id: UUID):
        pipe = self.redis.pipeline()
        now = datetime.now()

        key = self._request_key(user_id, now.minute)

        pipe.incr(key)
        pipe.expire(key, 60)
        result = pipe.execute(False)
        return result[0]


def create_fast_db(app) -> RedisDB:

    host = app.config.get('REDIS_HOST')
    port = app.config.get('REDIS_PORT')

    refresh_token_expiration = app.config.get('JWT_REFRESH_TOKEN_EXPIRATION')

    return RedisDB(
        refresh_token_expiration=refresh_token_expiration,
        redis_connection=redis.Redis(host=host, port=port)
    )
