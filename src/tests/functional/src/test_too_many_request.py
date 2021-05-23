import requests
from http import HTTPStatus


def test_too_many_request_logout(jwt_headers, clear_request_limit, logout_url):
    too_many_request(jwt_headers, logout_url, 'post')


def test_too_many_request_refresh_url(jwt_headers, clear_request_limit, refresh_url):
    too_many_request(jwt_headers, refresh_url, 'post')


def test_too_many_request_check_user(jwt_headers, clear_request_limit, check_user_url):
    too_many_request(jwt_headers, check_user_url, 'post')


def test_too_many_request_update_data(jwt_headers, clear_request_limit, update_data_url):
    too_many_request(jwt_headers, update_data_url, 'post')


def test_too_many_request_user_data(jwt_headers, clear_request_limit, user_data_url):
    too_many_request(jwt_headers, user_data_url, 'get')


def too_many_request(jwt_headers, url, method):

    for i in range(0, 51):
        _ = requests.request(
            method,
            url,
            headers=jwt_headers
        )

    resp = requests.request(
            method,
            url,
            headers=jwt_headers
        )

    assert resp.status_code == HTTPStatus.TOO_MANY_REQUESTS
