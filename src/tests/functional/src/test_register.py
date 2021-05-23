from http import HTTPStatus
import json


def test_register_user(session, user, register_url):
    resp = session.post(
        register_url,
        data=json.dumps(user),
        headers={
            'content-type': 'application/json'
        }
    )

    assert resp.status_code == HTTPStatus.OK
    date = resp.json()
    keys = date.keys()
    assert 'first_name' in keys
    assert 'last_name' in keys
    assert date.get('email', None) == user.get('email')
    assert date.get('password', None) == user.get('password')


def test_register_user_wrong_format(session, register_url):
    resp = session.post(
        register_url,
        data=json.dumps({
            'mail': 'example@ex.com',
            'password': 'qwerty'
        }),
        headers={
            'content-type': 'application/json'
        }
    )

    assert resp.status_code == HTTPStatus.BAD_REQUEST
    bad_email = 'example.com'

    resp = session.post(
        register_url,
        data=json.dumps({
            'email': bad_email,
            'password': 'qwerty'
        }),
        headers={
            'content-type': 'application/json'
        }
    )

    assert resp.status_code == HTTPStatus.BAD_REQUEST


def test_register_user_exists(session, another_user, register_url):
    resp = session.post(
        register_url,
        data=json.dumps(another_user),
        headers={
            'content-type': 'application/json'
        }
    )

    assert resp.status_code == HTTPStatus.OK

    resp = session.post(
        register_url,
        data=json.dumps(another_user),
        headers={
            'content-type': 'application/json'
        }
    )

    assert resp.status_code == HTTPStatus.CONFLICT
    data = resp.json()

    assert data.get('email', '') == another_user.get('email')
