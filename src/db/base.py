import uuid
from abc import ABC, abstractmethod
from flask import current_app


class FastDB(ABC):

    def __init__(self, refresh_token_expiration: int):
        self.refresh_token_expiration = refresh_token_expiration

    @abstractmethod
    def get_user_request_count(self, user_id: uuid.UUID) -> int:
        pass

    @abstractmethod
    def get_session_data(self, session_id: uuid.UUID):
        pass

    @abstractmethod
    def add_user_session(self, user_id: uuid.UUID, session_expiration: int):
        pass

    @abstractmethod
    def pop_session(self, session_id):
        pass

    @abstractmethod
    def add_jwt_refresh_token(self, user_id: uuid.UUID, refresh_token: uuid.UUID):
        pass

    @abstractmethod
    def check_jwt_refresh_token(self, user_id, refresh_token):
        pass

    @abstractmethod
    def clear_all_refresh_token(self, user_id):
        pass

    def _gen_session_id(self) -> uuid.UUID:
        return uuid.uuid4()
