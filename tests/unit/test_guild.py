import pytest

from flask_discord import configs
from flask_discord.models import Guild
from flask_discord.models.base import DiscordModelsBase


@pytest.fixture
def payload():
    return {'id': 1,
            'name': 'test_name',
            'icon': 'test_icon_hash',
            'is_owner': False}


@pytest.fixture
def guild(payload):
    return Guild(payload)


@pytest.fixture
def guild_no_icon_hash(payload):
    del payload['icon']
    return Guild(payload)


def test_icon_url(guild):
    assert guild.icon_url == configs.DISCORD_GUILD_ICON_BASE_URL.format(guild_id=guild.id, icon_hash=guild.icon_hash)


def test_icon_url_none(guild_no_icon_hash):
    assert guild_no_icon_hash.icon_url is None


def test_fetch_from_api_no_cache(guild, mocker):
    mocker.patch.object(DiscordModelsBase, 'fetch_from_api', return_value=[])
    assert guild.fetch_from_api(cache=False) == []