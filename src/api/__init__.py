from flask import Blueprint

from .health import get_status
from .v1 import routes

api_bp = Blueprint('api', __name__, url_prefix='/api')

api_bp.add_url_rule('/v1/register', view_func=routes.register, methods=('POST',), endpoint='register')
api_bp.add_url_rule('/v1/login', view_func=routes.login, methods=('POST',), endpoint='login')
api_bp.add_url_rule('/v1/2f_auth/sync', view_func=routes.sync_2f_auth, methods=('GET',), endpoint='sync_2f_auth')
api_bp.add_url_rule('/v1/2f_auth/check', view_func=routes.check_2f_auth, methods=('POST',), endpoint='check_2f_auth')

api_bp.add_url_rule('/v1/logout', view_func=routes.logout, methods=('POST',), endpoint='logout')
api_bp.add_url_rule('/v1/check_user', view_func=routes.check_user, methods=('POST',), endpoint='check_user')
api_bp.add_url_rule('/v1/refresh', view_func=routes.refresh, methods=('POST',), endpoint='refresh')

api_bp.add_url_rule('/v1/update_data', view_func=routes.update_user_data, methods=('POST',), endpoint='update_data')
api_bp.add_url_rule('/v1/user_data', view_func=routes.user_data, methods=('GET',), endpoint='user_data')

api_bp.add_url_rule('/v1/swagger', view_func=routes.swagger_json_api, methods=('GET',), endpoint='swagger_json')

