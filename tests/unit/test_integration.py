import pytest

from flask_discord.models import Integration

test_payload_full = {
    'id': 1,
    'name': 'test',
    'type': 'test',
    'enabled': 'test',
    'syncing': 'test',
    'role_id': 1,
    'account': 'test',
    'synced_at': 12000,
    'expire_behaviour': 'test',
    'expire_grace_period': 10000}

test_payload_no_id = {
    'name': 'test',
    'type': 'test',
    'enabled': 'test',
    'syncing': 'test',
    'role_id': 1,
    'account': 'test',
    'synced_at': 12000,
    'expire_behaviour': 'test',
    'expire_grace_period': 10000}

test_payload_no_role_id = {
    'id': 1,
    'name': 'test',
    'type': 'test',
    'enabled': 'test',
    'syncing': 'test',
    'account': 'test',
    'synced_at': 12000,
    'expire_behaviour': 'test',
    'expire_grace_period': 10000}


@pytest.mark.parametrize("test_payload", [test_payload_full, test_payload_no_id, test_payload_no_role_id])
def test_integration(test_payload):
    integration = Integration(test_payload)

    assert integration.id == test_payload.get('id', 0)
    assert integration.name == test_payload.get('name')
    assert integration.type == test_payload.get('type')
    assert integration.enabled == test_payload.get('enabled')
    assert integration.syncing == test_payload.get('syncing')
    assert integration.role_id == test_payload.get('role_id', 0)
    assert integration.account == test_payload.get('account')
    assert integration.synced_at == test_payload.get('synced_at')
    assert integration.expire_behaviour == test_payload.get('expire_behaviour')
    assert integration.expire_grace_period == test_payload.get('expire_grace_period')
