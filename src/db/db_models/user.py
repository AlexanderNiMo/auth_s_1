import datetime
import uuid

from sqlalchemy.dialects.postgresql import UUID

from db import db


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    login = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)

    first_name = db.Column(db.String, nullable=True)
    last_name = db.Column(db.String, nullable=True)

    otp_key = db.Column(db.String, nullable=True)

    history = db.relationship("UserSignIn")

    def __repr__(self):
        return f'<User {self.login}>'


def create_partition(target, connection, **kw) -> None:
    """ creating partition by user_sign_in """
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "login_history_smart" PARTITION OF "login_history" FOR VALUES IN ('smart')"""
    )
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "login_history_mobile" PARTITION OF "login_history" FOR VALUES IN ('mobile')"""
    )
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "login_history_web" PARTITION OF "login_history" FOR VALUES IN ('web')"""
    )


class UserSignIn(db.Model):
    __tablename__ = 'login_history'
    __table_args__ = {
        'postgresql_partition_by': 'LIST (user_device_type)',
        'listeners': [('after_create', create_partition)],
    }

    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'))

    logined_by = db.Column(db.DateTime, default=datetime.datetime.utcnow, primary_key=True)
    user_agent = db.Column(db.Text)
    user_device_type = db.Column(db.Text, nullable=False, primary_key=True)

    def __repr__(self):
        return f'<UserSignIn {self.user_id}:{self.logined_by}>'
