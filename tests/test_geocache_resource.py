from datetime import date

import pytest

from otbp.models import db, GeoCacheModel
from otbp.utils import geodistance

from tests.support.assertions import validate_json


@pytest.fixture
def test_geocache(app, client, test_user):
    # there is no geocache in the database already, so one should be created

    point = (42.38, -83.84)  # lat, lng tuple

    # hit the api
    rv = client.get(f'/geocache/{point[0]},{point[1]}',
                    headers=test_user.auth_headers)

    json_data = rv.get_json()

    return json_data


def test_get_new_geocache(app, client, test_user):
    # there is no geocache in the database already, so one should be created

    point = (42.38, -83.84)  # lat, lng tuple

    # hit the api
    rv = client.get(f'/geocache/{point[0]},{point[1]}',
                    headers=test_user.auth_headers)

    assert rv.status_code == 200

    json_data = rv.get_json()

    validate_json(json_data, 'geocache.json')

    with app.app_context():
        assert GeoCacheModel.query.count() == 1

        geocache = GeoCacheModel.query.first()

        distance = geodistance(point[0], point[1], geocache.lat, geocache.lng)

        # check that the distance is correct
        assert distance <= app.config['TARGET_MAX_DISTANCE']
        assert distance >= app.config['TARGET_MIN_DISTANCE']

        # check that the date is correct - it should match today's date
        assert date.today() == geocache.created_at.date()


def test_get_existing_geocache(app, client, test_user, test_geocache):
    # there is a geocache in the database already, so one should NOT be created

    point = (42.38, -83.84)  # lat, lng tuple

    # hit the api
    rv = client.get(f'/geocache/{point[0]},{point[1]}',
                    headers=test_user.auth_headers)

    assert rv.status_code == 200

    json_data = rv.get_json()

    assert test_geocache == json_data

    validate_json(json_data, 'geocache.json')

    with app.app_context():
        assert GeoCacheModel.query.count() == 1

        geocache = GeoCacheModel.query.first()

        distance = geodistance(point[0], point[1], geocache.lat, geocache.lng)

        # check that the distance is correct
        assert distance <= app.config['TARGET_MAX_DISTANCE']
        assert distance >= app.config['TARGET_MIN_DISTANCE']

        # check that the date is correct - it should match today's date
        assert date.today() == geocache.created_at.date()
