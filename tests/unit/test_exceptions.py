import pytest

from flask_discord import Unauthorized, AccessDenied, HttpException, RateLimited


def raise_http_exception():
    raise HttpException()


def raise_rate_limited(json, headers):
    raise RateLimited(json, headers)


def raise_unauthorized():
    raise Unauthorized()


def raise_access_denied():
    raise AccessDenied()


def test_http_exception():
    with pytest.raises(HttpException):
        raise_http_exception()


def test_rate_limited():
    json = {'message': 'test_message', 'global': 'test', 'retry_after': '10000'}
    headers = {'user-agent': 'test/0.0.1'}

    with pytest.raises(RateLimited) as ex_info:
        raise_rate_limited(json, headers)

    assert ex_info.value.message == json['message']
    assert ex_info.value.is_global == json["global"]
    assert ex_info.value.retry_after == json["retry_after"]
    assert ex_info.value.headers['user-agent'] == headers['user-agent']


def test_unauthorized():
    with pytest.raises(Unauthorized):
        raise_unauthorized()


def test_access_denied():
    with pytest.raises(AccessDenied):
        raise_access_denied()
