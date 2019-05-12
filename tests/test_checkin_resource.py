import pytest

from otbp.models import db, GeocacheModel, CheckInModel

from tests.support.assertions import validate_json


@pytest.fixture
def test_location(app):
    with app.app_context():
        location = GeocacheModel(lat=42.0, lng=42.0)
        db.session.add(location)
        db.session.commit()

        return location.id


@pytest.fixture
def test_other_location(app):
    with app.app_context():
        location = GeocacheModel(lat=84.0, lng=84.0)
        db.session.add(location)
        db.session.commit()

        return location.id


@pytest.fixture
def test_checkins(app, test_user, test_other_user, test_location, test_photo, test_other_location):
    with app.app_context():
        db.session.add(CheckInModel(text='test user, test location, no image',
                                    lat=1.0,
                                    lng=1.0,
                                    final_distance=2.0,
                                    user_id=test_user.id,
                                    geocache_id=test_location))

        db.session.add(CheckInModel(text='test user, test location, test image',
                                    lat=1.0,
                                    lng=1.0,
                                    final_distance=2.0,
                                    user_id=test_user.id,
                                    image_id=test_photo,
                                    geocache_id=test_location))

        db.session.add(CheckInModel(text='test user, test other location, no image',
                                    lat=1.0,
                                    lng=1.0,
                                    final_distance=2.0,
                                    user_id=test_user.id,
                                    geocache_id=test_other_location))

        db.session.add(CheckInModel(text='test other user, test location, no image',
                                    lat=1.0,
                                    lng=1.0,
                                    final_distance=2.0,
                                    user_id=test_other_user.id,
                                    geocache_id=test_location))

        db.session.add(CheckInModel(text='test other user, test other location, no image',
                                    lat=1.0,
                                    lng=1.0,
                                    final_distance=2.0,
                                    user_id=test_other_user.id,
                                    geocache_id=test_other_location))

        db.session.commit()


def test_create_checkin_without_image(app, client, test_user, test_location):
    data = {
        'geocache_id': test_location,
        'text': 'Hello, world!',
        'location': {
            'lat': 42.1,
            'lng': 42.1
        }
    }

    # hit the api
    rv = client.post(f'/checkin/',
                     json=data,
                     headers=test_user.auth_headers)

    assert rv.status_code == 201

    with app.app_context():
        checkin = CheckInModel.query.filter_by(user_id=test_user.id).order_by(CheckInModel.created_at.desc()).first()

        assert checkin.text == data['text']
        assert checkin.lat == data['location']['lat']
        assert checkin.lng == data['location']['lng']
        assert checkin.geocache_id == test_location
        assert checkin.image is None


def test_create_checkin_with_image(app, client, test_user, test_location, test_photo):
    data = {
        'geocache_id': test_location,
        'text': 'Hello, world!',
        'location': {
            'lat': 42.1,
            'lng': 42.1
        },
        'image_id': test_photo
    }

    # hit the api
    rv = client.post(f'/checkin/',
                     json=data,
                     headers=test_user.auth_headers)

    assert rv.status_code == 201

    with app.app_context():
        checkin = CheckInModel.query.filter_by(user_id=test_user.id).order_by(CheckInModel.created_at.desc()).first()

        assert checkin.text == data['text']
        assert checkin.lat == data['location']['lat']
        assert checkin.lng == data['location']['lng']
        assert checkin.geocache_id == test_location
        assert checkin.image_id == test_photo


def test_create_checkin_without_geocache(app, client, test_user):
    data = {
        'text': 'Hello, world!',
        'location': {
            'lat': 42.1,
            'lng': 42.1
        },
    }

    # hit the api
    rv = client.post(f'/checkin/',
                     json=data,
                     headers=test_user.auth_headers)

    assert rv.status_code == 422


def test_create_checkin_without_location(app, client, test_user, test_location):
    data = {
        'geocache_id': test_location,
        'text': 'Hello, world!',
    }

    # hit the api
    rv = client.post(f'/checkin/',
                     json=data,
                     headers=test_user.auth_headers)

    assert rv.status_code == 422


@pytest.mark.usefixtures('test_checkins')
def test_retrieve_user_checkins_paginated(app, client, test_user):
    # hit the api
    rv = client.get(f'/checkin/user/{test_user.id}',
                    headers=test_user.auth_headers)

    assert rv.status_code == 200

    json_data = rv.get_json()

    validate_json(json_data, 'checkins-paginated.json')

    # confirm that user checkins are only for this user
    for checkin in json_data['items']:
        assert checkin['user']['id'] == test_user.id


@pytest.mark.usefixtures('test_checkins')
def test_prevent_other_user_retrieve_user_checkins_paginated(app, client, test_user, test_other_user):
    # hit the api
    rv = client.get(f'/checkin/user/{test_other_user.id}',
                    headers=test_user.auth_headers)

    assert rv.status_code == 401