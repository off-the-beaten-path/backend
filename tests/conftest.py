from collections import namedtuple

import io
import pytest

from otbp import create_app
from otbp.models import db, UserModel
from otbp.praetorian import guard


@pytest.fixture
def app():
    flask_app = create_app()
    flask_app.testing = True

    with flask_app.app_context():
        db.drop_all()

        db.create_all()

        yield flask_app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


@pytest.fixture
def test_user(app):
    TestUser = namedtuple(
        'TestUser', ['email', 'password', 'id', 'auth_headers']
    )

    with app.app_context():
        email = 'test@unittest.com'
        password = 'password123'

        user = UserModel(email=email,
                         password=guard.encrypt_password(password),
                         roles='player')

        db.session.add(user)
        db.session.commit()

        headers = {'Authorization': f'Bearer {guard.encode_jwt_token(user)}'}

        return TestUser(email=email,
                        password=password,
                        id=user.id,
                        auth_headers=headers)


@pytest.fixture
def test_other_user(app):
    TestUser = namedtuple(
        'TestUser', ['email', 'password', 'id', 'auth_headers']
    )

    with app.app_context():
        email = 'test2@unittest.com'
        password = 'password123'

        user = UserModel(email=email,
                         password=guard.encrypt_password(password),
                         roles='player')

        db.session.add(user)
        db.session.commit()

        headers = {'Authorization': f'Bearer {guard.encode_jwt_token(user)}'}

        return TestUser(email=email,
                        password=password,
                        id=user.id,
                        auth_headers=headers)


@pytest.fixture
def test_image(app, client, test_user):
    data = {
        'file': (io.BytesIO(b'abcdef'), 'test.jpg')
    }

    with app.app_context():
        # hit the api
        rv = client.post('/image/',
                         data=data,
                         content_type='multipart/form-data',
                         headers=test_user.auth_headers)

        return rv.get_json()['id']


@pytest.fixture
def test_other_image(app, client, test_user):
    data = {
        'file': (io.BytesIO(b'ghijklmnop'), 'another.jpg')
    }

    with app.app_context():
        # hit the api
        rv = client.post('/image/',
                         data=data,
                         content_type='multipart/form-data',
                         headers=test_user.auth_headers)

        return rv.get_json()['id']


@pytest.fixture
def test_other_user_image(app, client, test_other_user):
    data = {
        'file': (io.BytesIO(b'rstuvz'), 'otheruser.jpg')
    }

    with app.app_context():
        # hit the api
        rv = client.post('/image/',
                         data=data,
                         content_type='multipart/form-data',
                         headers=test_other_user.auth_headers)

        return rv.get_json()['id']
