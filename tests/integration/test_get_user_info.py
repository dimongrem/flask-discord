from types import SimpleNamespace

import flask
import pytest
from flask import jsonify
from werkzeug.exceptions import abort

from flask_discord import DiscordOAuth2Session
from flask_discord.models import User, UserConnection
from flask_discord.models.base import DiscordModelsBase


@pytest.fixture
def user_payload():
    return {'id': 1,
            'username': 'test_username',
            'discriminator': '1000',
            'avatar': 'test_avatar',
            'bot': False,
            'mfa_enabled': False,
            'locale': 'test_locale',
            'verified': False,
            'email': 'test_email',
            'flags': 100,
            'premium_type': 100}


@pytest.fixture
def user_full(user_payload):
    return User(user_payload)


@pytest.fixture
def user_connection_payload():
    return {'id': 1,
            'name': 'test_name',
            'type': 'test_type',
            'revoked': False,
            'verified': False,
            'friend_sync': False,
            'show_activity': False,
            'visibility': 1}


@pytest.fixture
def user_connection(user_connection_payload):
    return UserConnection(user_connection_payload)


@pytest.fixture
def app(monkeypatch):
    app = flask.Flask(__name__)
    app.config['TESTING'] = True
    app.secret_key = b"%\xe0'\x01\xdeH\x8e\x85m|\xb3\xffCN\xc9g"
    monkeypatch.setenv('OAUTHLIB_INSECURE_TRANSPORT', 'true')

    app.config["DISCORD_CLIENT_ID"] = 490732332240863233
    app.config["DISCORD_CLIENT_SECRET"] = "TEST_DISCORD_CLIENT_SECRET"
    app.config["DISCORD_BOT_TOKEN"] = "TEST_DISCORD_BOT_TOKEN"
    app.config["DISCORD_REDIRECT_URI"] = "http://127.0.0.1:5000/callback"

    discord = DiscordOAuth2Session(app)

    @app.route("/me/")
    def me():
        user = discord.fetch_user()
        if user is None:
            abort(401)

        return jsonify(
            user_name=user.name,
            avatar_url=user.avatar_url or user.default_avatar_url,
            is_avatar_animated=user.is_avatar_animated
        )

    @app.route("/me/connections/")
    def my_connections():
        user = discord.fetch_user()
        connections = discord.fetch_connections()
        if user is None or connections is None:
            abort(401)

        return jsonify(
            user_name=user.name,
            connections=[f"{connection.name} - {connection.type}" for connection in connections]
        )

    @app.route("/me/guilds/")
    def user_guilds():
        guilds = discord.fetch_guilds()
        guilds = guilds.return_value

        return "<br />".join([f"[ADMIN] {g.name}" if g.permissions.administrator else g.name for g in guilds])

    @app.route("/add_to/<int:guild_id>/")
    def add_to_guild(guild_id):
        user = discord.fetch_user()
        return user.add_to_guild(guild_id)

    return app


def test_get_user_info_unauthorized(app, user_full, mocker):
    with app.app_context():
        app.discord = SimpleNamespace()
        app.discord.authorized = False

        mocker.patch('flask.current_app', return_value=app)

        mocker.patch.object(User, 'get_from_cache', return_value=None)
        mocker.patch.object(User, 'fetch_from_api', return_value=None)

        with app.test_client() as client:
            response = client.get('/me/')
            assert response.status_code == 401


def test_get_user_info_authorized(app, user_full, mocker):
    with app.app_context():
        app.discord = SimpleNamespace()
        app.discord.authorized = True

        mocker.patch('flask.current_app', return_value=app)

        mocker.patch.object(User, 'get_from_cache', return_value=user_full)
        mocker.patch.object(User, 'fetch_from_api', return_value=user_full)

        with app.test_client() as client:
            response = client.get('/me/')
            assert response.status_code == 200
            assert response.json['user_name'] == user_full.name
            assert response.json['avatar_url'] == user_full.avatar_url
            assert response.json['is_avatar_animated'] == user_full.is_avatar_animated


def test_get_user_connections_unauthorized(app, user_full, mocker):
    with app.app_context():
        app.discord = SimpleNamespace()
        app.discord.authorized = False

        mocker.patch('flask.current_app', return_value=app)

        mocker.patch.object(User, 'get_from_cache', return_value=None)
        mocker.patch.object(User, 'fetch_from_api', return_value=None)
        mocker.patch.object(UserConnection, 'fetch_from_api', return_value=None)

        with app.test_client() as client:
            response = client.get('/me/connections/')
            assert response.status_code == 401


def test_get_user_connections_authorized(app, user_full, user_connection, mocker):
    with app.app_context():
        app.discord = SimpleNamespace()
        app.discord.authorized = True
        app.discord.user_id = user_full.id
        app.discord.users_cache = {user_full.id: user_full}

        mocker.patch('flask.current_app', return_value=app)

        mocker.patch.object(User, 'get_from_cache', return_value=user_full)
        mocker.patch.object(User, 'fetch_from_api', return_value=user_full)
        mocker.patch.object(DiscordModelsBase, 'fetch_from_api', return_value=[user_connection])

        with app.test_client() as client:
            response = client.get('/me/connections/')
            assert response.status_code == 200
            assert response.json['user_name'] == user_full.name
            assert response.json['connections'] == [f"{user_connection.name} - {user_connection.type}"]