from http import HTTPStatus
from json import dumps

from flask import request, jsonify, make_response, redirect, url_for, abort, current_app

from services import EmailExists, WrongPassword, JWTService, OTPService, SessionService, UserController
from .utils import required_refresh_token, required_session_id, verify_user_data, required_jwt_auth, limit_requests


def register():
    user = verify_user_data()

    controller = UserController()
    try:
        controller.register_user(user)
    except EmailExists as ex:
        resp = make_response()
        resp.status_code = HTTPStatus.CONFLICT
        resp.set_data(ex.json())
        resp.headers = {
            'content-type': 'application/json'
        }
        return resp

    data = user.dict()
    data.pop('password')

    return jsonify(data)


def login():
    user = verify_user_data()

    controller = UserController()

    db_user = controller.get_user_data(user)

    if db_user is None or not controller.check_user_password(db_user, user.password):
        resp = make_response()
        resp.status_code = HTTPStatus.BAD_REQUEST
        resp.headers = {
            'content-type': 'application/json'
        }
        resp.set_data(
            dumps({'message': 'wrong login or password'})
        )
        return resp

    session_controller = SessionService()
    session_id, expires = session_controller.create_session(db_user)

    resp = make_response()
    resp.headers = {
        'Set-Cookie': f'SESSION_ID={session_id}; Path=/; HttpOnly; Expires={expires}',
        'SESSION_ID': f'{session_id}'
    }

    return resp


@required_session_id
@limit_requests
def sync_2f_auth(db_user):

    if db_user.otp_key is not None:
        resp = make_response()
        resp.status_code = HTTPStatus.BAD_REQUEST
        resp.headers = {
            'content-type': 'application/json'
        }
        resp.set_data(
            dumps({'message': 'user already have otp key'})
        )
        return resp

    otp_controller = OTPService()
    provisioning_url = otp_controller.get_provisioning_url(db_user)
    return jsonify(
        {'url': provisioning_url}
    )


@required_session_id
@limit_requests
def check_2f_auth(db_user):

    data = request.json
    code = data.get('code', None)

    if code is None:
        resp = make_response()
        resp.status_code = HTTPStatus.BAD_REQUEST
        resp.headers = {
            'content-type': 'application/json'
        }
        resp.set_data(dumps({'message': 'no otp code!'}))
        return resp

    if db_user.otp_key is None:
        return redirect(url_for('api.sync_2f_auth'))

    otp_controller = OTPService()

    if not otp_controller.check_otp_code(db_user=db_user, otp_code=int(code)):
        resp = make_response()
        resp.status_code = HTTPStatus.BAD_REQUEST
        resp.headers = {
            'content-type': 'application/json'
        }
        resp.set_data(dumps({'message': 'wrong otp code!'}))
        return resp

    user_controller = UserController()
    user_controller.add_login_record(db_user, request.user_agent.string, request.user_agent.platform)

    jwt_controller = JWTService()

    return jsonify(jwt_controller.generate_jwt_pair(user_id=db_user.id))


@required_jwt_auth
@limit_requests
def logout(db_user):
    jwt_controller = JWTService()
    jwt_controller.expire_all_refresh_tokens(db_user.id)

    resp = make_response()
    resp.status_code = HTTPStatus.OK

    return resp


@required_jwt_auth
@limit_requests
def check_user(db_user):
    return jsonify(dict(
        email=db_user.login,
        id=db_user.id,
        first_name=db_user.first_name,
        last_name=db_user.last_name,
    ))


@required_refresh_token
@limit_requests
def refresh(user_id, refresh_token):
    jwt_controller = JWTService()
    new_data = jwt_controller.refresh_jwt(user_id, refresh_token)
    if not new_data:
        abort(HTTPStatus.UNAUTHORIZED)
    return jsonify(new_data)


@required_jwt_auth
@limit_requests
def update_user_data(db_user):
    user_data = request.json
    user = verify_user_data(user_data.get('user'))

    controller = UserController()
    try:
        controller.update_user_data(db_user, user, user_data.get('old_password'))
    except EmailExists as ex:
        resp = make_response()
        resp.status_code = HTTPStatus.CONFLICT
        resp.set_data(ex.json())
        resp.headers = {
            'content-type': 'application/json'
        }
        return resp
    except WrongPassword as ex:
        resp = make_response()
        resp.status_code = HTTPStatus.UNAUTHORIZED
        resp.set_data(ex.json())
        resp.headers = {
            'content-type': 'application/json'
        }
        return resp

    return jsonify(user.dict())


@required_jwt_auth
@limit_requests
def user_data(db_user):
    return jsonify(
        {
            'id': db_user.id,
            'email': db_user.login,
            'first_name': db_user.first_name,
            'last_name': db_user.last_name,
            'history': [
                {
                    'logined_by': el.logined_by,
                    'user_device_type': el.user_device_type,
                    'user_agent': el.user_agent
                } for el in db_user.history
            ]
        }
    )


def swagger_json_api():
    api_file = current_app.config.get('SWAGGER_CONFIG_FILE', f'{current_app.config.root_path}/api/v1/openapi.json')
    with open(api_file, r'r') as f:
        return f.read()
