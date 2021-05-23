import datetime
from models.user import User
import hashlib
import os
import json
from typing import Optional
import pyotp
import jwt
from uuid import uuid4, UUID
from flask import current_app

from db import db
from db.db_models import User as db_User, UserSignIn
from sqlalchemy.exc import IntegrityError
from .base import EmailExists, WrongPassword
from db import fast_db


class UserController:

    def __init__(self):
        self.hash_iteration = 100000

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


class SessionController:

    def __init__(self):
        self.session_expiration = 10*60

    def create_session(self, db_user: db_User):
        session_id = fast_db.add_user_session(db_user.id, self.session_expiration)
        return session_id, expiration_from_now(self.session_expiration)

    def check_session_id(self, session_id) -> Optional[str]:
        return fast_db.get_session_data(session_id)


class OTPController:

    def get_provisioning_url(self, db_user):
        user_id = db_user.id
        secret = pyotp.random_base32()
        self._set_user_otp_key(db_user, secret)
        totp = pyotp.TOTP(secret)
        return totp.provisioning_uri(name=str(user_id) + '@kino_no.ru', issuer_name='Awesome cinema')

    def check_otp_code(self, db_user: db_User, otp_code: str):
        totp = pyotp.TOTP(db_user.otp_key)
        return totp.verify(otp_code)

    def _set_user_otp_key(self, db_user: db_User, otp_key: str):
        db_user.otp_key = otp_key
        db.session.add(db_user)
        db.session.commit()


class JWTController:

    def __init__(self):
        self._secret = current_app.config.get('JWT_SECRET')
        self.jwt_token_expiration = 15 * 60

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


class RequestController:

    def __init__(self):
        self.request_limit = 50

    def check_user_limit(self, user_id):
        return fast_db.get_user_request_count(user_id) < self.request_limit


def expiration_from_now(expiration_in_seconds: int):
    expires = datetime.datetime.now() + datetime.timedelta(seconds=expiration_in_seconds)
    return expires.strftime('%a, %d %b %Y %H:%M:%S GMT')


def parse_expiration(expiration_in_html_format: str):
    return datetime.datetime.strptime(expiration_in_html_format, '%a, %d %b %Y %H:%M:%S GMT')