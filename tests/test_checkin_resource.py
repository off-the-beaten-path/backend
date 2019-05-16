from datetime import date, timedelta
from freezegun import freeze_time

import operator
import pytest

from otbp.models import db, GeoCacheModel, CheckInModel
from otbp.utils import geodistance

from tests.support.assertions import validate_json


@pytest.fixture
def test_location(app):
    with app.app_context():
        location = GeoCacheModel(lat=42.0, lng=42.0)
        db.session.add(location)
        db.session.commit()

        return location.id


@pytest.fixture
def test_other_location(app):
    with app.app_context():
        location = GeoCacheModel(lat=84.0, lng=84.0)
        db.session.add(location)
        db.session.commit()

        return location.id


@pytest.fixture
def test_checkins(app, test_user, test_other_user, test_location, test_image, test_other_location):
    with app.app_context():
        checkins = [
            CheckInModel(text='test user, test location, no image',
                         lat=1.0,
                         lng=1.0,
                         final_distance=2.0,
                         user_id=test_user.id,
                         geocache_id=test_location),
            CheckInModel(text='test user, test location, test image',
                         lat=1.0,
                         lng=1.0,
                         final_distance=2.0,
                         user_id=test_user.id,
                         image_id=test_image,
                         geocache_id=test_location),
            CheckInModel(text='test user, test other location, no image',
                         lat=1.0,
                         lng=1.0,
                         final_distance=2.0,
                         user_id=test_user.id,
                         geocache_id=test_other_location),
            CheckInModel(text='test other user, test location, no image',
                         lat=1.0,
                         lng=1.0,
                         final_distance=2.0,
                         user_id=test_other_user.id,
                         geocache_id=test_location),
            CheckInModel(text='test other user, test other location, no image',
                         lat=1.0,
                         lng=1.0,
                         final_distance=2.0,
                         user_id=test_other_user.id,
                         geocache_id=test_other_location)
        ]

        db.session.add_all(checkins)

        db.session.commit()

        return list(map(operator.attrgetter('id'), checkins))


def test_create_checkin_without_image(app, client, test_user, test_location):
    data = {
        'geocache_id': test_location,
        'text': 'Hello, world!',
        'location': {
            'lat': 42.00001,
            'lng': 42.00001
        }
    }

    # hit the api
    rv = client.post(f'/checkin/',
                     json=data,
                     headers=test_user.auth_headers)

    assert rv.status_code == 201

    with app.app_context():
        checkin = CheckInModel.query.filter_by(user_id=test_user.id).order_by(CheckInModel.created_at.desc()).first()
        geocache = GeoCacheModel.query.get(test_location)

        assert checkin.text == data['text']
        assert checkin.lat == data['location']['lat']
        assert checkin.lng == data['location']['lng']
        assert checkin.geocache_id == test_location
        assert checkin.image is None

        # confirm that the final distance is correct - an approximation due to floating point arithmetic
        assert abs(checkin.final_distance - geodistance(geocache.lat, geocache.lng, data['location']['lat'],
                                                        data['location']['lng'])) < 0.01


def test_create_checkin_with_image(app, client, test_user, test_location, test_image):
    data = {
        'geocache_id': test_location,
        'text': 'Hello, world!',
        'location': {
            'lat': 42.00001,
            'lng': 42.00001
        },
        'image_id': test_image
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
        assert checkin.image_id == test_image


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


def test_create_checkin_with_old_geocache(app, client, test_user, test_location):
    data = {
        'geocache_id': test_location,
        'text': 'Hello, world!',
        'location': {
            'lat': 42.1,
            'lng': 42.1
        },
    }

    today = date.today()
    future = today + timedelta(days=1)

    # move one day into the future in order to test that expired (geocaches are valid only on the date of creation)
    # geocaches cannot be checked into
    with freeze_time(future):
        # hit the api
        rv = client.post(f'/checkin/',
                         json=data,
                         headers=test_user.auth_headers)

        assert rv.status_code == 400


def test_create_checkin_too_far_away(app, client, test_user, test_location):
    # attempt to check in while laughably far away
    data = {
        'geocache_id': test_location,
        'text': 'Hello, world!',
        'location': {
            'lat': 0.1,
            'lng': 0.1
        }
    }

    # hit the api
    rv = client.post(f'/checkin/',
                     json=data,
                     headers=test_user.auth_headers)

    assert rv.status_code == 400


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
    rv = client.get(f'/checkin/user/paginated',
                    headers=test_user.auth_headers)

    assert rv.status_code == 200

    json_data = rv.get_json()

    validate_json(json_data, 'checkins-paginated.json')

    # confirm that user checkins are only for this user
    with app.app_context():
        for checkin in json_data['items']:
            assert CheckInModel.query.get(checkin['id']).user.id == test_user.id


@pytest.mark.usefixtures('test_checkins')
def test_retrieve_user_checkins_all(app, client, test_user):
    # hit the api
    rv = client.get(f'/checkin/user/',
                    headers=test_user.auth_headers)

    assert rv.status_code == 200

    json_data = rv.get_json()

    validate_json(json_data, 'checkins.json')

    # confirm that user checkins are only for this user
    with app.app_context():
        for checkin in json_data['items']:
            assert CheckInModel.query.get(checkin['id']).user.id == test_user.id


def test_retrieve_user_checkin(app, client, test_user, test_checkins):
    checkin_id, *_ = test_checkins

    # hit the api
    rv = client.get(f'/checkin/user/{checkin_id}',
                    headers=test_user.auth_headers)

    assert rv.status_code == 200

    json_data = rv.get_json()

    validate_json(json_data, 'checkin.json')

    # confirm that user checkins are only for this user
    with app.app_context():
        assert CheckInModel.query.get(json_data['id']).user.id == test_user.id
