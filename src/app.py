# from gevent import monkey
# monkey.patch_all()

from flask import Flask
from flask_cors import CORS
import db
from flask_swagger_ui import get_swaggerui_blueprint
import json


def create_app():
    app = Flask('auth_service')

    app.config.from_pyfile("local.cfg", silent=True)

    db.init_db(app)
    db.fast_db = db.create_fast_db(app)

    app.register_blueprint(create_swaggerui_blueprint(app))

    from .api import api_bp
    app.register_blueprint(api_bp)

    return app


def create_swaggerui_blueprint(app):

    swagger_config_file = app.config.get('SWAGGER_CONFIG_FILE', f'{app.config.root_path}/src/api/v1/openapi.json')

    with open(swagger_config_file, r'r') as f:
       swagger_config = json.load(f)

    swaggerui_blueprint = get_swaggerui_blueprint(
        app.config.get('SWAGGER_URL', '/api/docs'),
        app.config.get('API_URL', '/api/v1'),
        config=swagger_config,

    )

    return swaggerui_blueprint


app = create_app()
CORS(app)
