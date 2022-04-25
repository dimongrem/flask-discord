import pytest

from flask_discord import configs
from flask_discord.models import User, UserConnection, Guild


@pytest.fixture
def payload():
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
def user_full(payload):
    return User(payload)


@pytest.fixture
def user_no_avatar(payload):
    payload = payload
    del payload['avatar']
    return User(payload)


@pytest.fixture
def user_anim_avatar(payload):
    payload['avatar'] = 'a_test_avatar'
    us = User(payload)
    return us


def test_guilds(user_full):
    guilds = {'test_key1': 'test_value1',
              'test_key2': 'test_value2',
              'test_key3': 'test_value3'}
    user_full.guilds = guilds
    assert user_full._guilds == guilds
    assert user_full.guilds == list(guilds.values())


def test_name(user_full):
    assert user_full.name == 'test_username'


@pytest.mark.skip(reason="Unreachable state")
def test_avatar_url_missing(user_no_avatar):
    assert user_no_avatar.avatar_url is None


def test_avatar_url(user_full):
    image_format = configs.DISCORD_ANIMATED_IMAGE_FORMAT \
        if user_full.is_avatar_animated else configs.DISCORD_IMAGE_FORMAT
    assert user_full.avatar_url == configs.DISCORD_USER_AVATAR_BASE_URL.format(
        user_id=user_full.id, avatar_hash=user_full.avatar_hash, format=image_format)


def test_default_avatar_url(user_full):
    assert user_full.default_avatar_url == configs.DISCORD_DEFAULT_USER_AVATAR_BASE_URL.format(
        modulo5=int(user_full.discriminator) % 5)


def test_is_avatar_animated_true(user_anim_avatar):
    assert user_anim_avatar.is_avatar_animated


def test_is_avatar_animated_false(user_full):
    assert not user_full.is_avatar_animated


def fetch_guilds(mocker):
    mocker.patch.object(Guild, 'fetch_from_api', return_value=[])
    assert user_full.fetch_guilds() == []


def test_fetch_connections(user_full, mocker):
    mocker.patch.object(UserConnection, 'fetch_from_api', return_value=[])

    assert user_full.fetch_connections() == []
