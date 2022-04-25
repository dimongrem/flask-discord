from types import SimpleNamespace
from urllib.parse import urlparse, parse_qs

import pytest

from flask_discord.configs import DISCORD_AUTHORIZATION_BASE_URL, DISCORD_OAUTH_DEFAULT_SCOPES
from flask_discord.models import User
from flask_discord.models.base import DiscordModelsBase


@pytest.mark.usefixtures("app")
@pytest.mark.usefixtures("test_user")
@pytest.mark.usefixtures("user_connection")
@pytest.mark.usefixtures("guild")
def test_once(app, test_user, user_connection, guild, mocker):
    with app.app_context():
        app.discord = SimpleNamespace()
        app.discord.authorized = True
        app.discord.user_id = test_user.id
        app.discord.users_cache = {test_user.id: test_user}
        app.discord.get_authorization_token = lambda: {'access_token': 'test_access_token'}
        app.discord.bot_request = lambda *args, **kwargs: False
        mocker.patch('flask.current_app', return_value=app)

        mocker.patch.object(User, 'get_from_cache', return_value=test_user)
        mocker.patch.object(User, 'fetch_from_api', return_value=test_user)
        mocker.patch.object(User, 'guilds', return_value=[guild])
        mocker.patch.object(DiscordModelsBase, 'fetch_from_api', return_value=[user_connection])

        with app.test_client() as client:
            # Test login
            response = client.get('/login/', follow_redirects=False)
            assert response.status_code == 302

            parsed_url = urlparse(response.location)
            assert parsed_url.scheme + '://' + parsed_url.hostname + parsed_url.path == \
                   DISCORD_AUTHORIZATION_BASE_URL

            parsed_query = parse_qs(parsed_url.query)
            assert parsed_query['response_type'][0] == 'code'
            assert parsed_query['client_id'][0] == str(app.config["DISCORD_CLIENT_ID"])
            assert parsed_query['redirect_uri'][0] == app.config["DISCORD_REDIRECT_URI"]
            assert parsed_query['scope'][0] == ' '.join(DISCORD_OAUTH_DEFAULT_SCOPES)

            # Test getting info about user
            response = client.get('/me/')
            assert response.status_code == 200
            assert response.json['user_name'] == test_user.name
            assert response.json['avatar_url'] == test_user.avatar_url
            assert response.json['is_avatar_animated'] == test_user.is_avatar_animated

            # Test getting info about user connections
            response = client.get('/me/connections/')
            assert response.status_code == 200
            assert response.json['user_name'] == test_user.name
            assert response.json['connections'] == [f"{user_connection.name} - {user_connection.type}"]

            # Test getting info about guilds
            response = client.get('/me/guilds/')
            assert response.status_code == 200
            assert response.data == b'test_name'

            # Test add to guild
            response = client.get('/add_to/1/')
            assert response.status_code == 200
            assert response.data == b'{}\n'

            # Test getting secret with auth guard
            response = client.get('/secret/')
            assert response.status_code == 200
            assert response.json['secret'] is not None

            # Test logout
            response = client.get('/logout/', follow_redirects=False)
            assert response.status_code == 302
            parsed_url = urlparse(response.location)
            assert parsed_url.hostname == 'localhost'
            assert parsed_url.path == '/'
