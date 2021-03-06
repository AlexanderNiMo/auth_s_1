import json
import os

from flask import Flask
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint

import db


def create_app():
    app = Flask('auth_service')

    load_config(app)

    db.init_db(app)
    db.fast_db = db.create_fast_db(app)

    app.register_blueprint(create_swaggerui_blueprint(app))

    from .api import api_bp, get_status
    app.register_blueprint(api_bp)
    app.add_url_rule('/api/health', view_func=get_status, methods=('GET',), endpoint='health')

    return app


def load_config(app):
    config_file = os.getenv("AUTH_CONFIG", "local_example.cfg")
    app.config.from_pyfile(config_file, silent=True)


def create_swaggerui_blueprint(app):

    swaggerui_blueprint = get_swaggerui_blueprint(
        app.config.get('SWAGGER_URL', '/api/docs'),
        app.config.get('API_URL', '/api/v1/swagger'),
    )

    return swaggerui_blueprint


app = create_app()
CORS(app)
