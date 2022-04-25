import pytest

from flask_discord.models import UserConnection
from flask_discord.models.base import DiscordModelsBase


@pytest.fixture
def payload():
    return {'id': 1,
            'name': 'test_name',
            'type': 'test_type',
            'revoked': False,
            'verified': False,
            'friend_sync': False,
            'show_activity': False,
            'visibility': 1}


@pytest.fixture
def user_connection_visible(payload):
    return UserConnection(payload)


@pytest.fixture
def user_connection_invisible(payload):
    payload['visibility'] = 0
    return UserConnection(payload)


def test_is_visible_true(user_connection_visible):
    assert user_connection_visible.is_visible


def test_is_visible_false(user_connection_invisible):
    assert not user_connection_invisible.is_visible


def test_fetch_from_api_no_cache(user_connection_visible, mocker):
    mocker.patch.object(DiscordModelsBase, 'fetch_from_api', return_value=[])
    assert user_connection_visible.fetch_from_api(cache=False) == []
