from types import SimpleNamespace

import flask
import pytest

from flask_discord import requires_authorization, Unauthorized, JSONBool, json_bool


@pytest.mark.parametrize("test_string", ['true', 'True', 'trUE'])
def test_from_string_true(test_string):
    assert JSONBool.from_string(test_string)


@pytest.mark.parametrize("test_string", ['false', 'False', 'fAlSe'])
def test_from_string_false(test_string):
    assert not JSONBool.from_string(test_string)


@pytest.mark.parametrize("test_string", ['gibberish', '12r3', 'flase', 'treu'])
def test_from_string_ex(test_string):
    with pytest.raises(ValueError):
        JSONBool.from_string(test_string)


@pytest.mark.parametrize("test_value", ['true', 'True', 'trUE', 1, 10])
def test_json_bool_true(test_value):
    assert json_bool(test_value) == 'true'


@pytest.mark.parametrize("test_value", ['false', 'False', 'fAlSe', 0])
def test_json_bool_false(test_value):
    assert json_bool(test_value) == 'false'


@pytest.mark.parametrize("test_value", ['gibberish', '12r3', 'flase', 'treu'])
def test_json_bool_ex(test_value):
    with pytest.raises(ValueError):
        json_bool(test_value)


def test_requires_authorization_true(mocker):
    view = lambda _: True
    app = flask.Flask(__name__)
    with app.app_context():
        app.discord = SimpleNamespace()
        app.discord.authorized = True
        mocker.patch('flask.current_app', return_value=app)

        ra_wrapper = requires_authorization(view)

        assert callable(ra_wrapper)
        assert ra_wrapper(view)


def test_requires_authorization_false(mocker):
    view = lambda _: True
    app = flask.Flask(__name__)
    with app.app_context():
        app.discord = SimpleNamespace()
        app.discord.authorized = False
        mocker.patch('flask.current_app', return_value=app)

        ra_wrapper = requires_authorization(view)

        assert callable(ra_wrapper)
        with pytest.raises(Unauthorized):
            ra_wrapper(view)
