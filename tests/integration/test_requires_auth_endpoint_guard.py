from types import SimpleNamespace

import flask
import pytest
from flask import jsonify

from flask_discord import requires_authorization, Unauthorized


@pytest.fixture
def app():
    app = flask.Flask(__name__)
    app.config['TESTING'] = True

    @app.route("/")
    @requires_authorization
    def index():
        return jsonify(
            authorized=True
        )

    return app


def test_endpoint_auth_accessible(app, mocker):
    with app.app_context():
        app.discord = SimpleNamespace()
        app.discord.authorized = True
        mocker.patch('flask.current_app', return_value=app)
        with app.test_client() as client:
            response = client.get('/')
            assert response.status_code == 200
            assert response.json['authorized']


def test_endpoint_auth_inaccessible(app, mocker):
    with app.app_context():
        app.discord = SimpleNamespace()
        app.discord.authorized = False
        mocker.patch('flask.current_app', return_value=app)
        with app.test_client() as client:
            with pytest.raises(Unauthorized):
                client.get('/')
