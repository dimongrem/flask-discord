from types import SimpleNamespace

import flask
import pytest

from flask_discord import DiscordOAuth2Session, Unauthorized
from flask_discord.models import User, Guild


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
def guild_payload():
    return {'id': 1,
            'name': 'test_name',
            'icon': 'test_icon_hash',
            'is_owner': False,
            }


@pytest.fixture
def guild_admin(guild_payload):
    guild_payload['permissions'] = '8'
    guild = Guild(guild_payload)
    return guild


@pytest.fixture
def guild_non_admin(guild_payload):
    guild_payload['permissions'] = '4294967296'
    guild = Guild(guild_payload)
    return guild


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


def test_get_user_guilds_unauthorized(app, user_full, mocker):
    with app.app_context():
        mocker.patch.object(User, 'get_from_cache', return_value=user_full)

        with app.test_client() as client:
            with pytest.raises(Unauthorized):
                client.get('/me/guilds/')


def test_get_user_guilds_authorized_admin(app, user_full, guild_admin, mocker):
    with app.app_context():
        app.discord = SimpleNamespace()
        app.discord.authorized = True
        mocker.patch('flask.current_app', return_value=app)

        mocker.patch.object(User, 'get_from_cache', return_value=user_full)
        mocker.patch.object(User, 'guilds', return_value=[guild_admin])

        with app.test_client() as client:
            response = client.get('/me/guilds/')
            assert response.status_code == 200
            assert response.data == b'[ADMIN] test_name'


def test_get_user_guilds_authorized_non_admin(app, user_full, guild_non_admin, mocker):
    with app.app_context():
        app.discord = SimpleNamespace()
        app.discord.authorized = True
        mocker.patch('flask.current_app', return_value=app)

        mocker.patch.object(User, 'get_from_cache', return_value=user_full)
        mocker.patch.object(User, 'guilds', return_value=[guild_non_admin])

        with app.test_client() as client:
            response = client.get('/me/guilds/')
            assert response.status_code == 200
            assert response.data == b'test_name'


def test_add_to_guild_unauthorized(app, user_full, guild_non_admin, mocker):
    with app.app_context():
        app.discord = SimpleNamespace()
        app.discord.authorized = False
        app.discord.get_authorization_token = lambda: {}
        mocker.patch('flask.current_app', return_value=app)

        mocker.patch.object(User, 'get_from_cache', return_value=user_full)
        mocker.patch.object(User, 'fetch_from_api', return_value=user_full)
        mocker.patch.object(User, 'guilds', return_value=[guild_admin])

        with app.test_client() as client:
            with pytest.raises(Unauthorized):
                client.get('/add_to/1/')


def test_add_to_guild_authorized(app, user_full, guild_non_admin, mocker):
    with app.app_context():
        app.discord = SimpleNamespace()
        app.discord.authorized = True
        app.discord.get_authorization_token = lambda: {'access_token': 'test_access_token'}

        app.discord.bot_request = lambda *args, **kwargs: False
        mocker.patch('flask.current_app', return_value=app)

        mocker.patch.object(User, 'get_from_cache', return_value=user_full)
        mocker.patch.object(User, 'fetch_from_api', return_value=user_full)
        mocker.patch.object(User, 'guilds', return_value=[guild_admin])

        with app.test_client() as client:
            response = client.get('/add_to/1/')
            assert response.status_code == 200
            assert response.data == b'{}\n'
