import pyotp

from db import db
from db.db_models import User as db_User
from .base import AppService


class OTPService(AppService):

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
