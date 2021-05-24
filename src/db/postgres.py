from flask import Flask
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


def init_db(app: Flask):
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:qwerty@localhost/auth'
    db.init_app(app)
    if app.config.get('TESTING', False):
        db.drop_all(app=app)
    db.create_all(app=app)
