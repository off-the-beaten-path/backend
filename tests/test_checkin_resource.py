from datetime import date, timedelta
from freezegun import freeze_time

import pytest

from otbp.models import db, GeoCacheModel, CheckInModel
from otbp.utils import geodistance

from tests.support.assertions import validate_json


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
    rv = client.post(f'/checkin',
                     json=data,
                     headers=test_user.auth_headers)

    assert rv.status_code == 201

    json_data = rv.get_json()

    validate_json(json_data, 'checkin.json')

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
    rv = client.post(f'/checkin',
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
    rv = client.post(f'/checkin',
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
        rv = client.post(f'/checkin',
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
    rv = client.post(f'/checkin',
                     json=data,
                     headers=test_user.auth_headers)

    assert rv.status_code == 400


def test_create_checkin_without_location(app, client, test_user, test_location):
    data = {
        'geocache_id': test_location,
        'text': 'Hello, world!',
    }

    # hit the api
    rv = client.post(f'/checkin',
                     json=data,
                     headers=test_user.auth_headers)

    assert rv.status_code == 422


@pytest.mark.usefixtures('test_checkins')
def test_create_checkin_previously_checked_in(app, client, test_user, test_location):
    data = {
        'geocache_id': test_location,
        'text': 'Hello, world!',
        'location': {
            'lat': 42.1,
            'lng': 42.1
        },
    }

    # hit the api
    rv = client.post(f'/checkin',
                     json=data,
                     headers=test_user.auth_headers)

    assert rv.status_code == 400


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


def test_retrieve_checkin(app, client, test_user, test_checkins):
    checkin_id, *_ = test_checkins

    # hit the api
    rv = client.get(f'/checkin/{checkin_id}',
                    headers=test_user.auth_headers)

    assert rv.status_code == 200

    json_data = rv.get_json()

    validate_json(json_data, 'checkin.json')

    # confirm that user checkins are only for this user
    with app.app_context():
        assert CheckInModel.query.get(json_data['id']).user.id == test_user.id


def test_retrieve_checkin_for_other_user(app, client, test_user, test_other_user, test_checkins):
    checkin_id, *_ = test_checkins

    # hit the api
    rv = client.get(f'/checkin/{checkin_id}',
                    headers=test_other_user.auth_headers)

    assert rv.status_code == 401

    json_data = rv.get_json()

    assert 'Unauthorized' in json_data['message']


def test_update_checkin(app, client, test_user, test_other_image, test_checkins):
    checkin_id, *_ = test_checkins

    data = {
        'text': 'Hello, world!',
        'image_id': test_other_image
    }

    rv = client.put(f'/checkin/{checkin_id}',
                    json=data,
                    headers=test_user.auth_headers)

    assert rv.status_code == 200

    json_data = rv.get_json()

    validate_json(json_data, 'checkin.json')

    assert json_data['text'] == data['text']
    assert json_data['image']['id'] == data['image_id']


def test_update_checkin_remove_image(app, client, test_user, test_checkins):
    checkin_id, *_ = test_checkins

    data = {
        'image_id': -1,
        'text': 'whatever the previous text was but i am too lazy to find it'
    }

    rv = client.put(f'/checkin/{checkin_id}',
                    json=data,
                    headers=test_user.auth_headers)

    assert rv.status_code == 200

    json_data = rv.get_json()

    validate_json(json_data, 'checkin.json')

    assert json_data['image'] is None


def test_update_checkin_other_user(app, client, test_user, test_other_user, test_checkins):
    checkin_id, *_ = test_checkins

    data = {
        'text': 'Hello, world!'
    }

    rv = client.put(f'/checkin/{checkin_id}',
                    json=data,
                    headers=test_other_user.auth_headers)

    assert rv.status_code == 401


def test_update_checkin_with_other_user_image(app, client, test_user, test_other_user_image, test_checkins):
    checkin_id, *_ = test_checkins

    data = {
        'text': 'Hello, world!',
        'image_id': test_other_user_image
    }

    rv = client.put(f'/checkin/{checkin_id}',
                    json=data,
                    headers=test_user.auth_headers)

    assert rv.status_code == 401
