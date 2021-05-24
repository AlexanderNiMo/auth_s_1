from functools import wraps
from http import HTTPStatus

from flask import request, make_response, abort
from pydantic import ValidationError

from models.user import User
from services import JWTService, RequestService, SessionService, UserController


def limit_requests(f):
    @wraps(f)
    def decorator(db_user, *args, **kwargs):
        user_id = db_user if type(db_user) == str else db_user.id
        request_controller = RequestService()
        if not request_controller.check_user_limit(user_id):
            return make_response('Too Many Requests!', HTTPStatus.TOO_MANY_REQUESTS)

        return f(db_user, *args, **kwargs)

    return decorator


def required_jwt_auth(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None

        if 'jwt_token' in request.headers:
            token = request.headers['jwt_token']

        if not token:
            return make_response('Could not verify token', HTTPStatus.UNAUTHORIZED)

        jwt_controller = JWTService()
        jwt_data = jwt_controller.check_jwt(token)

        if not jwt_data:
            return make_response('Could not verify token', HTTPStatus.UNAUTHORIZED)

        user_controller = UserController()
        db_user = user_controller.get_user_by_id(jwt_data.get('user_id'))

        if db_user is None:
            resp = make_response()
            resp.status_code = HTTPStatus.UNAUTHORIZED
            return abort(resp)

        return f(db_user, *args, **kwargs)

    return decorator


def required_refresh_token(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        refresh_token = None
        jwt_token = None

        if 'refresh_token' in request.headers:
            refresh_token = request.headers['refresh_token']

        if 'jwt_token' in request.headers:
            jwt_token = request.headers['jwt_token']

        jwt_controller = JWTService()
        jwt_data = jwt_controller.get_jwt_data(jwt_token)
        if not jwt_data:
            abort(HTTPStatus.UNAUTHORIZED)

        user_id = jwt_data.get('user_id')

        return f(user_id, refresh_token, *args, **kwargs)

    return decorator


def required_session_id(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        session_id = request.cookies.get('SESSION_ID')

        if session_id is None:
            resp = make_response()
            resp.status_code = HTTPStatus.UNAUTHORIZED
            return abort(resp)

        session_controller = SessionService()
        user_id = session_controller.check_session_id(session_id)

        if user_id is None:
            resp = make_response()
            resp.status_code = HTTPStatus.UNAUTHORIZED
            return abort(resp)

        user_controller = UserController()
        db_user = user_controller.get_user_by_id(user_id)

        if db_user is None:
            resp = make_response()
            resp.status_code = HTTPStatus.UNAUTHORIZED
            return abort(resp)

        return f(db_user, *args, **kwargs)

    return decorator


def check_jwt_token(token_data=None):
    if not token_data:
        token_data = request.json
        token_data = token_data.get('jwt_token')
        token_data = token_data.get('token')
    jwt_controller = JWTService()
    return jwt_controller.check_jwt(token_data)


def verify_user_data(data=None):
    try:
        if data:
            user = User(**data)
        else:
            user = User(**request.json)
    except ValidationError as ex:
        resp = make_response()
        resp.status_code = HTTPStatus.BAD_REQUEST
        resp.headers = {
            'content-type': 'application/json'
        }
        resp.set_data(ex.json())
        return abort(resp)

    return user