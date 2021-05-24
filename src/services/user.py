import datetime
import hashlib
import json
import os
from typing import Optional

from sqlalchemy.exc import IntegrityError

from db import db
from db.db_models import User as db_User, UserSignIn
from models.user import User
from .base import AppService
from .base import EmailExists, WrongPassword


class UserController(AppService):

    def __init__(self):
        super(UserController, self).__init__()
        self.hash_iteration = self.app_config.get('HASH_ITERATIONS')

    def register_user(self, user: User):
        try:
            db_user = db_User(
                login=user.email,
                password=self._get_password_data(user.password),
                first_name=user.first_name,
                last_name=user.last_name
            )
            db.session.add(db_user)
            db.session.commit()
        except IntegrityError as ex:
            raise EmailExists(user.email)

    def update_user_data(self, db_user: db_User, user: User, old_password: str):

        if not self.check_user_password(db_user, old_password):
            raise WrongPassword(old_password)

        if user.password:
            db_user.password = self._get_password_data(user.password)

        if user.first_name:
            db_user.first_name = user.first_name

        if user.last_name:
            db_user.last_name = user.last_name

        if user.email:
            db_user.login = user.email

        db.session.add(db_user)
        try:
            db.session.commit()
        except IntegrityError as ex:
            raise EmailExists(user.email)

    def get_user_data(self, user: User) -> db_User:
        return db_User.query.filter_by(login=user.email).first()

    def get_user_by_id(self, user_id):
        return db_User.query.filter_by(id=user_id).first()

    def check_user_password(self, user: db_User, password):
        password_data = json.loads(user.password)

        password_data['salt'] = bytes.fromhex(password_data.get('salt'))
        password_data['key'] = bytes.fromhex(password_data.get('key'))

        return password_data['key'] == self._crypt_password(
            password,
            password_data['salt'],
            password_data['iterations']
        )

    def add_login_record(self, user: db_User, user_agent: str, user_device_type: Optional[str]):

        user.history.append(
            UserSignIn(
                logined_by=datetime.datetime.utcnow(),
                user_agent=user_agent,
                user_device_type='mobile' if not user_device_type else user_device_type)
        )

        db.session.add(user)
        db.session.commit()

    def _get_password_data(self, password: str):

        salt = os.getrandom(32)

        return json.dumps(
            {
                'key': self._crypt_password(password, salt).hex(),
                'salt': salt.hex(),
                'iterations': self.hash_iteration
            }
        )

    def _crypt_password(self, password: str, salt: bytes, iterations: Optional[int] = None) -> bytes:

        if iterations is None:
            iterations = self.hash_iteration

        return hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt,
            iterations
        )
