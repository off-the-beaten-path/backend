from datetime import date, datetime

import pytest

from otbp.models import db, GeoCacheModel, CheckInModel
from otbp.utils import geodistance

from tests.support.assertions import validate_json


@pytest.fixture
def test_geocache(app, test_user):
    with app.app_context():
        geocache = GeoCacheModel(lat=42.38, lng=-83.84, user_id=test_user.id)
        db.session.add(geocache)
        db.session.commit()

        return geocache.id


@pytest.fixture
def test_geocaches(app, test_user):
    with app.app_context():
        geocaches = []

        for i in range(10):
            geocache = GeoCacheModel(lat=42.38 + i, lng=-83.84 + i, user_id=test_user.id)
            geocaches.append(geocache)
            db.session.add(geocache)

        db.session.commit()

        return [geocache.id for geocache in geocaches]


def test_create_geocache(app, client, test_user):
    data = {
        'lat': 42.38,
        'lng': -83.84
    }

    # hit the api
    rv = client.post(f'/geocache',
                     json=data,
                     headers=test_user.auth_headers)

    assert rv.status_code == 200

    json_data = rv.get_json()

    validate_json(json_data, 'geocache.json')

    with app.app_context():
        assert GeoCacheModel.query.count() == 1

        geocache = GeoCacheModel.query.first()

        distance = geodistance(data['lat'], data['lng'], geocache.lat, geocache.lng)

        # check that the distance is correct
        assert distance <= app.config['TARGET_MAX_DISTANCE']
        assert distance >= app.config['TARGET_MIN_DISTANCE']

        # check that the date is correct - it should match today's date
        assert date.today() == geocache.created_at.date()


def test_create_geocache_deletes_inactive_previous(app, client, test_user, test_geocache, test_geocaches):
    with app.app_context():
        # create a checkin to make this geocache inactive
        # this geocache should not be removed by the purge
        checkin = CheckInModel(lat=42, lng=43, final_distance=44, geocache_id=test_geocache, user_id=test_user.id)
        db.session.add(checkin)
        db.session.commit()

    # test geocaches should be removed by purge

    data = {
        'lat': 42.38,
        'lng': -83.84
    }

    # hit the api
    rv = client.post(f'/geocache',
                     json=data,
                     headers=test_user.auth_headers)

    assert rv.status_code == 200

    json_data = rv.get_json()

    validate_json(json_data, 'geocache.json')

    with app.app_context():
        assert GeoCacheModel.query.get(test_geocache) is not None

        for geocache_id in test_geocaches:
            assert GeoCacheModel.query.get(geocache_id) is None


def test_get_active_geocache_for_user(app, client, test_user, test_geocache):
    rv = client.get(f'/geocache/active',
                    headers=test_user.auth_headers)

    assert rv.status_code == 200

    json_data = rv.get_json()

    validate_json(json_data, 'geocache.json')


def test_get_active_geocache_for_user_sort_by_created(app, client, test_user, test_geocaches):
    rv = client.get(f'/geocache/active',
                    headers=test_user.auth_headers)

    assert rv.status_code == 200

    json_data = rv.get_json()

    validate_json(json_data, 'geocache.json')

    with app.app_context():
        target_id = json_data['id']
        target = GeoCacheModel.query.get(target_id)

        for geocache_id in test_geocaches:
            if target_id != geocache_id:
                geocache = GeoCacheModel.query.get(geocache_id)

                assert target.created_at >= geocache.created_at


def test_get_active_geocache_for_user_no_geocaches_in_db(app, client, test_user):
    rv = client.get(f'/geocache/active',
                    headers=test_user.auth_headers)

    assert rv.status_code == 404


def test_get_active_geocache_for_user_no_valid_geocaches(app, client, test_user, test_geocache):
    with app.app_context():
        # create a checkin to make this geocache inactive
        checkin = CheckInModel(lat=42, lng=43, final_distance=44, geocache_id=test_geocache, user_id=test_user.id)
        db.session.add(checkin)
        db.session.commit()

    rv = client.get(f'/geocache/active',
                    headers=test_user.auth_headers)

    assert rv.status_code == 404
