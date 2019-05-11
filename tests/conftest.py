import pytest

from otbp import create_app
from otbp.models import db


@pytest.fixture
def app():
    flask_app = create_app()
    flask_app.testing = True

    with flask_app.app_context():
        db.create_all()

    yield flask_app

    with flask_app.app_context():
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()
