import os

import flask
import pytest
from flask import jsonify, url_for
from werkzeug.exceptions import abort
from werkzeug.utils import redirect

from flask_discord import DiscordOAuth2Session, requires_authorization
from flask_discord.models import User, UserConnection, Guild


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
def test_user(user_payload):
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
def guild_payload():
    return {'id': 1,
            'name': 'test_name',
            'icon': 'test_icon_hash',
            'is_owner': False,
            'permissions': '4294967296'
            }


@pytest.fixture
def guild(guild_payload):
    guild = Guild(guild_payload)
    return guild


@pytest.fixture
def app(monkeypatch):
    app = flask.Flask(__name__)
    app.config['TESTING'] = True
    app.secret_key = b"%\xe0'\x01\xdeH\x8e\x85m|\xb3\xffCN\xc9g"
    monkeypatch.setenv('OAUTHLIB_INSECURE_TRANSPORT', 'true')

    app.config["DISCORD_CLIENT_ID"] = 836357504018677810
    app.config["DISCORD_CLIENT_SECRET"] = "vPX6jZdr1e1c74vB-JLZE1V1vU0EKoFF"
    app.config["DISCORD_BOT_TOKEN"] = "ODM2MzU3NTA0MDE4Njc3ODEw.YIc0nw.vGlRUnpML0-upoG83Vy3DindqyM"
    app.config["DISCORD_REDIRECT_URI"] = "http://127.0.0.1:5000/callback"

    discord = DiscordOAuth2Session(app)

    @app.route("/")
    def index():
        pass

    @app.route("/login/")
    def login():
        return discord.create_session()

    @app.route("/logout/")
    def logout():
        discord.revoke()
        return redirect(url_for(".index"))

    @app.route("/callback/")
    def callback():
        data = discord.callback()
        redirect_to = data.get("redirect", "/me/")

        return redirect(redirect_to)

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

    @app.route("/secret/")
    @requires_authorization
    def secret():
        return jsonify(
            secret=str(os.urandom(16))
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
