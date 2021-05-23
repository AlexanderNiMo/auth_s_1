from http import HTTPStatus
import json
from uuid import UUID
import pytest


def test_login_user(session, registered_user, login_url, register_url):

    resp = session.post(
        login_url,
        data=json.dumps(registered_user),
        headers={
            'content-type': 'application/json'
        }
    )

    assert resp.status_code == HTTPStatus.OK
    session_id = next((c for c in resp.cookies if c.name == 'SESSION_ID'), None)
    assert session_id is not None
    assert UUID(session_id.value) is not None


wrong_data = [
    {'email': 'example3ex.com'},
    {'password': '111'},
]


@pytest.mark.parametrize('upd_data', wrong_data)
def test_login_user_wrong_data(session, registered_user, login_url, upd_data):

    registered_user.update(upd_data)

    resp = session.post(
        login_url,
        data=json.dumps(registered_user),
        headers={
            'content-type': 'application/json'
        }
    )

    assert resp.status_code == HTTPStatus.BAD_REQUEST
    session_id = resp.cookies.get('SESSION_ID')
    assert session_id is None


def test_2f_sync(authorised_session, sync_2f_url):
    resp = authorised_session.get(
        sync_2f_url,
        headers={
            'content-type': 'application/json'
        }
    )

    assert resp.status_code == HTTPStatus.OK
    data = resp.json()
    assert data.get('url')

    resp = authorised_session.get(
        sync_2f_url,
        headers={
            'content-type': 'application/json'
        }
    )

    assert resp.status_code == HTTPStatus.BAD_REQUEST
    data = resp.json()
    assert data.get('message') == 'user already have otp key'


def test_2f_sync_unauthorised(session, sync_2f_url):
    resp = session.get(
        sync_2f_url,
        headers={
            'content-type': 'application/json'
        }
    )

    assert resp.status_code == HTTPStatus.UNAUTHORIZED


def test_2f_check(otp_session_and_key, check_2f_url):
    session, otp_key = otp_session_and_key

    resp = session.post(
        check_2f_url,
        headers={
            'content-type': 'application/json'
        },
        data=json.dumps({'code': otp_key}),
    )

    assert resp.status_code == HTTPStatus.OK
    data = resp.json()
    assert 'jwt_token' in data.keys()
    assert 'refresh_token' in data.keys()


def test_logout(session, jwt_headers, logout_url, refresh_url):
    resp = session.post(
        logout_url,
        headers=jwt_headers
    )

    assert resp.status_code == HTTPStatus.OK

    resp = session.post(
        refresh_url,
        headers=jwt_headers
    )

    assert resp.status_code == HTTPStatus.UNAUTHORIZED


def test_logout_unauthorised(session, wrong_jwt_headers, logout_url):
    resp = session.post(
        logout_url,
        headers=wrong_jwt_headers
    )

    assert resp.status_code == HTTPStatus.UNAUTHORIZED
