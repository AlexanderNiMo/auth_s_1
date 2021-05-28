import time
from http import HTTPStatus

from pytest import fixture
import requests
import json
import pyotp
from .utils import clear_db, clear_redis_request_limit
from .testdata import get_config


@fixture
def user() -> dict:
    return {
        'email': 'example@ex.com',
        'password': 'example',
        'first_name': 'Ivan',
        'last_name': 'Ivanov'
    }


@fixture
def user3():
    return {
        'email': 'example3@ex.com',
        'password': 'example2',
        'first_name': 'Ivan',
        'last_name': 'Ivanov'
    }


@fixture
def registered_user(session, register_url) -> dict:
    user_data = {
        'email': 'example2@ex.com',
        'password': 'example2',
        'first_name': 'Ivan',
        'last_name': 'Ivanov'
    }

    _ = requests.post(
        register_url,
        data=json.dumps(user_data),
        headers={
            'content-type': 'application/json'
        }
    )

    return user_data


@fixture
def login_user_cookies(session, registered_user, login_url):
    resp = session.post(
        login_url,
        data=json.dumps(registered_user),
        headers={
            'content-type': 'application/json'
        }
    )

    return resp.cookies


@fixture
def another_user() -> dict:
    return {
        'email': 'example_2@ex.com',
        'password': 'example'
    }


@fixture
def wrong_credentials() -> dict:
    return {
        'email': '',
        'password': ''
    }


@fixture
def session(clear_request_limit) -> requests.Session:
    session = requests.Session()
    return session


@fixture
def authorised_session(login_user_cookies) -> requests.Session:
    session = requests.Session()
    session.cookies = login_user_cookies
    return session


@fixture
def otp_session_and_key(session, register_url, login_url, sync_2f_url, check_2f_url, user3, drop_base):

    user_data = user3

    _ = session.post(
        register_url,
        data=json.dumps(user_data),
        headers={
            'content-type': 'application/json'
        }
    )

    _ = session.post(
        login_url,
        data=json.dumps(user_data),
        headers={
            'content-type': 'application/json'
        }
    )

    resp = session.get(
        sync_2f_url,
        headers={
            'content-type': 'application/json'
        }
    )

    data = resp.json()
    url_data = pyotp.parse_uri(data.get('url'))
    totp = pyotp.TOTP(url_data.secret)

    while True:
        otp_code = totp.now()

        resp = session.post(
            check_2f_url,
            headers={
                'content-type': 'application/json'
            },
            data=json.dumps({'code': otp_code}),
        )

        if resp.status_code == HTTPStatus.OK:
            break

        time.sleep(1)

    return session,  otp_code


@fixture
def jwt_token_refresh_token(otp_session_and_key, check_2f_url) -> dict:

    session, otp_key = otp_session_and_key

    resp = session.post(
        check_2f_url,
        headers={
            'content-type': 'application/json'
        },
        data=json.dumps({'code': otp_key}),
    )

    data = resp.json()

    return data


@fixture
def jwt_headers(jwt_token_refresh_token):
    headers = {'content-type': 'application/json'}
    headers.update(jwt_token_refresh_token)
    return headers


@fixture
def wrong_jwt_headers():
    headers = {'content-type': 'application/json'}
    headers.update({
        "jwt_token": "123",
        "refresh_token": "123"
    })
    return headers


@fixture
def drop_base(config):
    clear_db(config)


@fixture
def clear_request_limit(config):
    clear_redis_request_limit(config)


@fixture
def jwt_token(jwt_token_refresh_token):
    return jwt_token_refresh_token.get('jwt_token')


@fixture
def config():
    return get_config()


@fixture
def root_url(config):
    return f'http://{config.auth_host}:{config.auth_port}/api/v1'


@fixture
def register_url(root_url) -> str:
    return f'{root_url}/register'


@fixture
def login_url(root_url):
    return f'{root_url}/login'


@fixture
def sync_2f_url(root_url):
    return f'{root_url}/2f_auth/sync'


@fixture
def check_2f_url(root_url):
    return f'{root_url}/2f_auth/check'


@fixture
def logout_url(root_url):
    return f'{root_url}/logout'


@fixture
def check_user_url(root_url):
    return f'{root_url}/check_user'


@fixture
def refresh_url(root_url):
    return f'{root_url}/refresh'


@fixture
def update_data_url(root_url):
    return f'{root_url}/update_data'


@fixture
def user_data_url(root_url):
    return f'{root_url}/user_data'


@fixture
def all_jwt_auth_urls(logout_url, refresh_url, check_user_url, update_data_url, user_data_url):
    return [logout_url, refresh_url, check_user_url, update_data_url, user_data_url]
