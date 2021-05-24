from flask import Flask
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


def init_db(app: Flask):
    postgres_user = app.config.get('POSTGRES_USER')
    postgres_password = app.config.get('POSTGRES_PASSWORD')
    postgres_host = app.config.get('POSTGRES_HOST')
    postgres_port = app.config.get('POSTGRES_PORT')

    app.config['SQLALCHEMY_DATABASE_URI'] = (f'postgresql://{postgres_user}:{postgres_password}@'
                                             f'{postgres_host}:{postgres_port}/auth')
    from .db_models import User, UserSignIn

    db.init_app(app)
    if app.config.get('TESTING', False):
        db.drop_all(app=app)
    db.create_all(app=app)
