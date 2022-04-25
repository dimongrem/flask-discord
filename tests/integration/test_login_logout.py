from urllib.parse import urlparse, parse_qs

import flask
import jwt
import pytest
from flask import url_for
from oauthlib.common import generate_token
from werkzeug.utils import redirect

from flask_discord import DiscordOAuth2Session, configs, json_bool
from flask_discord.configs import DISCORD_OAUTH_DEFAULT_SCOPES


@pytest.fixture
def data_login_with_data():
    return dict(redirect="/me/", coupon="15off", number=15, zero=0, status=False)


@pytest.fixture
def data_invite_bot():
    return dict(scope=["bot"], permissions=8, guild_id=464488012328468480,
                disable_guild_select=True)


@pytest.fixture
def data_invite_oauth():
    return dict(scope=["bot", "identify"], permissions=8)


@pytest.fixture
def app(monkeypatch, data_login_with_data, data_invite_bot, data_invite_oauth):
    app = flask.Flask(__name__)
    app.config['TESTING'] = True
    app.secret_key = b"%\xe0'\x01\xdeH\x8e\x85m|\xb3\xffCN\xc9g"
    monkeypatch.setenv('OAUTHLIB_INSECURE_TRANSPORT', 'true')

    app.config["DISCORD_CLIENT_ID"] = 490732332240863233
    app.config["DISCORD_CLIENT_SECRET"] = "TEST_DISCORD_CLIENT_SECRET"
    app.config["DISCORD_BOT_TOKEN"] = "TEST_DISCORD_BOT_TOKEN"
    app.config["DISCORD_REDIRECT_URI"] = "http://127.0.0.1:5000/callback"

    discord = DiscordOAuth2Session(app)

    @app.route("/")
    def index():
        pass

    @app.route("/login/")
    def login():
        return discord.create_session()

    @app.route("/login-prompt/")
    def login_prompt():
        return discord.create_session(scope=data_invite_bot['scope'], prompt=False)

    @app.route("/login-data/")
    def login_with_data():
        return discord.create_session(data=data_login_with_data)

    @app.route("/invite-bot/")
    def invite_bot():
        return discord.create_session(scope=data_invite_bot['scope'],
                                      permissions=data_invite_bot['permissions'],
                                      guild_id=data_invite_bot['guild_id'],
                                      disable_guild_select=data_invite_bot['disable_guild_select'])

    @app.route("/invite-bot-invalid-permissions/")
    def invite_bot_invalid_permissions():
        return discord.create_session(scope=data_invite_bot['scope'],
                                      permissions='raise_value_error',
                                      guild_id=data_invite_bot['guild_id'],
                                      disable_guild_select=data_invite_bot['disable_guild_select'])

    @app.route("/invite-oauth/")
    def invite_oauth():
        return discord.create_session(scope=data_invite_oauth['scope'], permissions=data_invite_oauth['permissions'])

    @app.route("/logout/")
    def logout():
        discord.revoke()
        return redirect(url_for(".index"))

    return app


def test_login(app, mocker):
    with app.app_context():
        mocker.patch('flask.current_app', return_value=app)

        with app.test_client() as client:
            response = client.get('/login/', follow_redirects=False)
            assert response.status_code == 302

            parsed_url = urlparse(response.location)
            assert parsed_url.scheme + '://' + parsed_url.hostname + parsed_url.path == \
                   configs.DISCORD_AUTHORIZATION_BASE_URL

            parsed_query = parse_qs(parsed_url.query)
            assert parsed_query['response_type'][0] == 'code'
            assert parsed_query['client_id'][0] == str(app.config["DISCORD_CLIENT_ID"])
            assert parsed_query['redirect_uri'][0] == app.config["DISCORD_REDIRECT_URI"]
            assert parsed_query['scope'][0] == ' '.join(DISCORD_OAUTH_DEFAULT_SCOPES)


def test_login_with_data(app, data_login_with_data, mocker):
    with app.app_context():
        mocker.patch('flask.current_app', return_value=app)
        mocker.patch.object(jwt, 'encode', return_value='test_generate_token')

        with app.test_client() as client:
            response = client.get('/login-data/', follow_redirects=False)
            assert response.status_code == 302

            parsed_url = urlparse(response.location)
            assert parsed_url.scheme + '://' + parsed_url.hostname + parsed_url.path == \
                   configs.DISCORD_AUTHORIZATION_BASE_URL

            parsed_query = parse_qs(parsed_url.query)
            assert parsed_query['response_type'][0] == 'code'
            assert parsed_query['client_id'][0] == str(app.config["DISCORD_CLIENT_ID"])
            assert parsed_query['redirect_uri'][0] == app.config["DISCORD_REDIRECT_URI"]
            assert parsed_query['scope'][0] == ' '.join(configs.DISCORD_OAUTH_DEFAULT_SCOPES)

            assert parsed_query['state'][0] == jwt.encode(data_login_with_data, app.config["SECRET_KEY"],
                                                          algorithm="HS256")


def test_invite_bot(app, data_invite_bot, mocker):
    with app.app_context():
        mocker.patch('flask.current_app', return_value=app)
        mocker.patch.object(jwt, 'encode', return_value='test_generate_token')

        with app.test_client() as client:
            response = client.get('/invite-bot/', follow_redirects=False)
            assert response.status_code == 302

            parsed_url = urlparse(response.location)
            assert parsed_url.scheme + '://' + parsed_url.hostname + parsed_url.path == \
                   configs.DISCORD_AUTHORIZATION_BASE_URL

            parsed_query = parse_qs(parsed_url.query)
            assert parsed_query['response_type'][0] == 'code'
            assert parsed_query['client_id'][0] == str(app.config["DISCORD_CLIENT_ID"])
            assert parsed_query['redirect_uri'][0] == app.config["DISCORD_REDIRECT_URI"]
            assert parsed_query['scope'][0] == data_invite_bot['scope'][0]
            assert parsed_query['guild_id'][0] == str(data_invite_bot['guild_id'])
            assert parsed_query['disable_guild_select'][0] == json_bool(data_invite_bot['disable_guild_select'])
            assert parsed_query['permissions'][0] == str(data_invite_bot['permissions'])

            data = dict()
            data["__state_secret_"] = generate_token()
            assert parsed_query['state'][0] == jwt.encode(data, app.config["SECRET_KEY"], algorithm="HS256")


def test_invite_oauth(app, data_invite_oauth, mocker):
    with app.app_context():
        mocker.patch('flask.current_app', return_value=app)
        mocker.patch.object(jwt, 'encode', return_value='test_generate_token')

        with app.test_client() as client:
            response = client.get('/invite-oauth/', follow_redirects=False)
            assert response.status_code == 302

            parsed_url = urlparse(response.location)
            assert parsed_url.scheme + '://' + parsed_url.hostname + parsed_url.path == \
                   configs.DISCORD_AUTHORIZATION_BASE_URL

            parsed_query = parse_qs(parsed_url.query)
            assert parsed_query['response_type'][0] == 'code'
            assert parsed_query['client_id'][0] == str(app.config["DISCORD_CLIENT_ID"])
            assert parsed_query['redirect_uri'][0] == app.config["DISCORD_REDIRECT_URI"]
            assert parsed_query['scope'][0] == ' '.join(data_invite_oauth['scope'])
            assert parsed_query['permissions'][0] == str(data_invite_oauth['permissions'])

            data = dict()
            data["__state_secret_"] = generate_token()
            assert parsed_query['state'][0] == jwt.encode(data, app.config["SECRET_KEY"], algorithm="HS256")


def test_logout(app, mocker):
    with app.app_context():
        mocker.patch('flask.current_app', return_value=app)

    with app.test_client() as client:
        response = client.get('/logout/', follow_redirects=False)
        assert response.status_code == 302
        parsed_url = urlparse(response.location)
        assert parsed_url.hostname is None
        assert parsed_url.path == '/'


def test_invite_bot_invalid_permissions(app, mocker):
    with app.app_context():
        mocker.patch('flask.current_app', return_value=app)
        mocker.patch.object(jwt, 'encode', return_value='test_generate_token')

        with app.test_client() as client:
            with pytest.raises(ValueError):
                client.get('/invite-bot-invalid-permissions/', follow_redirects=False)


def test_login_prompt(app, mocker):
    with app.app_context():
        mocker.patch('flask.current_app', return_value=app)
        mocker.patch.object(jwt, 'encode', return_value='test_generate_token')

        with app.test_client() as client:
            with pytest.raises(ValueError):
                client.get('/login-prompt/', follow_redirects=False)
