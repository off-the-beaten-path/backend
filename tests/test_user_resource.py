from datetime import date, timedelta
from freezegun import freeze_time

import pytest

from otbp.models import UserModel
from otbp.praetorian import guard

from tests.support.assertions import validate_json


@pytest.mark.parametrize(
    ('email', 'password'),
    (
            ('example@example.com', 'password123'),
            ('pinky@pinky.me', 'pinkisthebestcolor')
    )
)
def test_register(app, client, email, password):
    # register payload
    data = {
        'email': email,
        'password': password
    }

    with app.app_context():
        # hit the api
        rv = client.post('/user/register',
                         json=data)

        assert rv.status_code == 201

        # confirm user is created in database
        user = UserModel.query.filter_by(email=data['email']).first()

        assert user.email == email
        assert guard._verify_password(password, user.password)
        assert user.rolenames == ['player']
        assert user.is_valid

        json_data = rv.get_json()

        # confirm login succeeded
        validate_json(json_data, 'user.jwt.json')


def test_register_existing_user(client, test_user):
    # register payload
    data = {
        'email': test_user.email,
        'password': test_user.password + 'abcdefg'  # note: different password
    }

    # hit the api
    rv = client.post('/user/register',
                     json=data)

    assert rv.status_code == 400
    assert 'already exists' in rv.get_json()['message']


@pytest.mark.parametrize(
    ('password', 'is_valid'),
    (
            ('short', False),
            ('', False),
            ('helloworld', True),
            ('tttttttttttttttttttttttttttttttt', True),
            ('tttttttttttttttttttttttttttttttt+', False),
    )
)
def test_register_user_with_bad_password(client, password, is_valid):
    # register payload
    data = {
        'email': 'example@example.org',
        'password': password
    }

    # hit the api
    rv = client.post('/user/register',
                     json=data)

    if is_valid:
        assert rv.status_code == 201
    else:
        assert rv.status_code == 400
        assert 'Invalid password' in rv.get_json()['message']


@pytest.mark.parametrize(
    ('email',),
    (
            ('bad',),
            ('bad@bad',),
    )
)
def test_register_user_with_bad_password(client, email):
    # register payload
    data = {
        'email': email,
        'password': 'verygoodnotsogreatpassword'
    }

    # hit the api
    rv = client.post('/user/register',
                     json=data)

    assert rv.status_code == 400
    assert 'Invalid email' in rv.get_json()['message']


def test_login(client, test_user):
    # login payload
    data = {
        'email': test_user.email,
        'password': test_user.password
    }

    # hit the api
    rv = client.post('/user/login',
                     json=data)

    assert rv.status_code == 200

    json_data = rv.get_json()

    # confirm login succeeded
    validate_json(json_data, 'user.jwt.json')


@pytest.mark.parametrize(
    ('email', 'password'),
    (
            ('short', 'tall'),
            ('', '')
    )
)
def test_login_invalid_account(client, email, password):
    # login payload
    data = {
        'email': email,
        'password': password
    }

    # hit the api
    rv = client.post('/user/login',
                     json=data)

    assert rv.status_code == 400
    assert 'Invalid email or password' in rv.get_json()['message']


def test_login_invalid_password(client, test_user):
    # login payload
    data = {
        'email': test_user.email,
        'password': test_user.password + 'abcdefg'  # note: different password
    }

    # hit the api
    rv = client.post('/user/login',
                     json=data)

    assert rv.status_code == 400
    assert 'Invalid email or password' in rv.get_json()['message']


def test_refresh(client, test_user):
    today = date.today()
    future = today + timedelta(days=5)

    # move five days into the future in order to avoid EarlyRefresh error
    with freeze_time(future):
        # hit the api
        rv = client.get('/user/refresh',
                        headers=test_user.auth_headers)

        assert rv.status_code == 200

        json_data = rv.get_json()

        # confirm refresh succeeded
        validate_json(json_data, 'user.jwt.json')


def test_change_password(client, test_user):
    # change password payload
    data = {
        'old': test_user.password,
        'new': 'this is a new and valid password!'
    }

    # hit the api
    rv = client.put('/user/password',
                    json=data,
                    headers=test_user.auth_headers)

    assert rv.status_code == 200

    # attempt to login with new password
    data = {
        'email': test_user.email,
        'password': data['new']
    }

    rv = client.post('/user/login',
                     json=data)

    assert rv.status_code == 200
    json_data = rv.get_json()

    # confirm login succeeded
    validate_json(json_data, 'user.jwt.json')


def test_invalid_change_password(client, test_user):
    # change password payload
    data = {
        'old': test_user.password + '42 makes it invalid',
        'new': 'this is a new and valid password!'
    }

    # hit the api
    rv = client.put('/user/password',
                    json=data,
                    headers=test_user.auth_headers)

    assert rv.status_code == 400

    assert 'Invalid password' in rv.get_json()['message']

    # attempt to login with new password
    data = {
        'email': test_user.email,
        'password': data['new']
    }

    rv = client.post('/user/login',
                     json=data)

    assert rv.status_code == 400

    # confirm login with new password failed
    assert 'Invalid email or password' in rv.get_json()['message']
