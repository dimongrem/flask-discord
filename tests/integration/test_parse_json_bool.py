import json
import pathlib

import pytest

from flask_discord import json_bool


@pytest.fixture
def test_json_data():
    test_json_path = pathlib.Path(__file__).parent.absolute() / 'test_data' / 'test_utils.json'
    with open(test_json_path, "r") as read_file:
        test_json_data = json.load(read_file)
        return test_json_data


def test_parse_json_bool_true(test_json_data):
    assert json_bool(test_json_data['users'][0]['verified']) == 'true'
    assert json_bool(test_json_data['users'][1]['bot']) == 'true'


def test_parse_json_bool_false(test_json_data):
    assert json_bool(test_json_data['users'][0]['bot']) == 'false'
    assert json_bool(test_json_data['users'][0]['mfa_enabled']) == 'false'


def test_parse_json_bool_ex(test_json_data):
    with pytest.raises(ValueError):
        json_bool(test_json_data['users'][1]['mfa_enabled'])

    with pytest.raises(ValueError):
        json_bool(test_json_data['users'][1]['verified'])
