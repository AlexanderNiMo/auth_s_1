import json
from http import HTTPStatus


def test_update_user_data(session, jwt_headers, update_data_url, user3):
    resp = session.patch(
        update_data_url,
        headers=jwt_headers,
        data=json.dumps(
            {
              "old_password": user3.get('password'),
              "user": {
                "email": user3.get('email'),
                "password": "password",
                "first_name": user3.get('first_name'),
                "last_name": user3.get('last_name')
              }
            }
        )
    )

    assert resp.status_code == HTTPStatus.OK


def test_update_user_data_wrong_password(session, jwt_headers, update_data_url, user3):
    resp = session.patch(
        update_data_url,
        headers=jwt_headers,
        data=json.dumps(
            {
              "old_password": '111',
              "user": {
                "email": user3.get('email'),
                "password": user3.get("password"),
                "first_name": user3.get('first_name'),
                "last_name": user3.get('last_name')
              }
            }
        )
    )

    assert resp.status_code == HTTPStatus.UNAUTHORIZED


def test_update_user_data_wrong_email(session, jwt_headers, update_data_url, user3, registered_user):
    resp = session.patch(
        update_data_url,
        headers=jwt_headers,
        data=json.dumps(
            {
              "old_password": user3.get("password"),
              "user": {
                "email": registered_user.get('email'),
                "password": user3.get("password"),
                "first_name": user3.get('first_name'),
                "last_name": user3.get('last_name')
              }
            }
        )
    )

    assert resp.status_code == HTTPStatus.CONFLICT


def test_get_user_data(session, jwt_headers, user_data_url):
    resp = session.get(
        user_data_url,
        headers=jwt_headers
    )

    assert resp.status_code == HTTPStatus.OK


def test_get_user_data_wrong_headers(session, wrong_jwt_headers, user_data_url):
    resp = session.get(
        user_data_url,
        headers=wrong_jwt_headers
    )

    assert resp.status_code == HTTPStatus.UNAUTHORIZED
