from http import HTTPStatus


def test_check_user(session, jwt_headers, check_user_url, user3):
    user3.pop('password')

    resp = session.post(
        check_user_url,
        headers=jwt_headers
    )

    assert resp.status_code == HTTPStatus.OK
    data = resp.json()
    assert 'id' in data.keys()
    data.pop('id')
    assert data == user3


def test_check_user_wrong_jwt(session, check_user_url, wrong_jwt_headers):

    resp = session.post(
        check_user_url,
        headers=wrong_jwt_headers
    )

    assert resp.status_code == HTTPStatus.UNAUTHORIZED


def test_refresh(session, jwt_headers, refresh_url):
    resp = session.post(
        refresh_url,
        headers=jwt_headers
    )

    assert resp.status_code == HTTPStatus.OK
    data = resp.json()
    assert 'jwt_token' in data.keys()
    assert 'refresh_token' in data.keys()


def test_refresh_wrong(session, drop_base, refresh_url, wrong_jwt_headers):
    resp = session.post(
        refresh_url,
        headers=wrong_jwt_headers
    )

    assert resp.status_code == HTTPStatus.UNAUTHORIZED
