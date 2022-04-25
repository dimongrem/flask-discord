import abc
import os
from types import SimpleNamespace

import pytest
import requests
from flask import Flask

from flask_discord import Unauthorized, RateLimited
from flask_discord._http import DiscordOAuth2HttpClient

DiscordOAuth2HttpClient.__abstractmethods__ = set()

assert isinstance(DiscordOAuth2HttpClient, abc.ABCMeta)


@pytest.fixture
def client_no_params():
    return DiscordOAuth2HttpClient()


@pytest.fixture
def app(mocker):
    app = Flask(__name__)
    mocker.patch.dict(os.environ, {"OAUTHLIB_INSECURE_TRANSPORT": "true"})
    app.config['SECRET_KEY'] = b"%\xe0'\x01\xdeH\x8e\x85m|\xb3\xffCN\xc9g"
    app.config["DISCORD_CLIENT_ID"] = 490732332240863233
    app.config["DISCORD_CLIENT_SECRET"] = 'TEST_CLIENT_SECRET'
    app.config["DISCORD_BOT_TOKEN"] = 'TEST_BOT_TOKEN'
    app.config["DISCORD_REDIRECT_URI"] = "http://127.0.0.1:5000/callback"

    return app


def test_init_app(client_no_params, app):
    assert client_no_params.init_app(app) is None


def test_save_authorization_token(client_no_params):
    with pytest.raises(NotImplementedError):
        client_no_params.save_authorization_token({})


def test_get_authorization_token(client_no_params):
    with pytest.raises(NotImplementedError):
        client_no_params.get_authorization_token()


def test__make_session(client_no_params):
    assert client_no_params._make_session(token='test_token', state='test_state', scope=['test_scope'])


def test_request_unauthorized(client_no_params, mocker):
    args_sn = {'status_code': 401}
    mocker.patch.object(requests, 'request', return_value=SimpleNamespace(**args_sn))
    with pytest.raises(Unauthorized):
        client_no_params.request(route='test_route', oauth=False)


def test_request_rate_limited(client_no_params, mocker):
    test_json = {'message': 'test_message', 'global': 'test', 'retry_after': '10000'}
    test_headers = {'user-agent': 'test/0.0.1'}
    args_sn = {'status_code': 429, 'json': lambda: test_json, 'headers': test_headers}

    mocker.patch.object(requests, 'request', return_value=SimpleNamespace(**args_sn))

    with pytest.raises(RateLimited) as ex_info:
        client_no_params.request(route='test_route', oauth=False)

    assert ex_info.value.message == test_json['message']
    assert ex_info.value.is_global == test_json["global"]
    assert ex_info.value.retry_after == test_json["retry_after"]
    assert ex_info.value.headers['user-agent'] == test_headers['user-agent']


def test_request(client_no_params, mocker):
    test_json = {'message': 'test_message', 'global': 'test', 'retry_after': '10000'}
    test_headers = {'user-agent': 'test/0.0.1'}
    args_sn = {'status_code': 200, 'json': lambda: test_json, 'headers': test_headers}

    mocker.patch.object(requests, 'request', return_value=SimpleNamespace(**args_sn))

    res_json = client_no_params.request(route='test_route', oauth=False)

    assert res_json['message'] == test_json['message']
    assert res_json['global'] == test_json["global"]
    assert res_json['retry_after'] == test_json["retry_after"]


def test_bot_request(client_no_params, mocker):
    test_json = {'message': 'test_message', 'global': 'test', 'retry_after': '10000'}
    args_sn = {'status_code': 200, 'json': lambda: test_json}

    mocker.patch.object(requests, 'request', return_value=SimpleNamespace(**args_sn))

    res_json = client_no_params.request(route='test_route', oauth=False)

    assert res_json['message'] == test_json['message']
    assert res_json['global'] == test_json["global"]
    assert res_json['retry_after'] == test_json["retry_after"]
