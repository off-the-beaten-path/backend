from datetime import date, timedelta

import pytest

from otbp.models import db, CheckInModel

from tests.support.assertions import validate_json


@pytest.fixture
def current_streak(app, test_user, test_location):
    with app.app_context():
        checkins = [
            # Today
            CheckInModel(text='test',
                         lat=1.0,
                         lng=1.0,
                         final_distance=2.0,
                         user_id=test_user.id,
                         geocache_id=test_location,
                         created_at=date.today() - timedelta(days=0)),

            # Yesterday
            CheckInModel(text='test',
                         lat=1.0,
                         lng=1.0,
                         final_distance=2.0,
                         user_id=test_user.id,
                         geocache_id=test_location,
                         created_at=date.today() - timedelta(days=1)),
        ]

        db.session.add_all(checkins)

        db.session.commit()

        return len(checkins)


@pytest.fixture
def longest_streak(app, test_user, test_location):
    with app.app_context():
        checkins = [
            # 5 Days ago
            CheckInModel(text='test',
                         lat=1.0,
                         lng=1.0,
                         final_distance=2.0,
                         user_id=test_user.id,
                         geocache_id=test_location,
                         created_at=date.today() - timedelta(days=5)),

            # 6 Days Ago
            CheckInModel(text='test',
                         lat=1.0,
                         lng=1.0,
                         final_distance=2.0,
                         user_id=test_user.id,
                         geocache_id=test_location,
                         created_at=date.today() - timedelta(days=6)),

            # 7 Days Ago
            CheckInModel(text='test',
                         lat=1.0,
                         lng=1.0,
                         final_distance=2.0,
                         user_id=test_user.id,
                         geocache_id=test_location,
                         created_at=date.today() - timedelta(days=7)),

            # 8 Days Ago
            CheckInModel(text='test',
                         lat=1.0,
                         lng=1.0,
                         final_distance=2.0,
                         user_id=test_user.id,
                         geocache_id=test_location,
                         created_at=date.today() - timedelta(days=8)),
        ]

        db.session.add_all(checkins)

        db.session.commit()

        return len(checkins)


@pytest.fixture
def multiple_checkins_one_day_current_streak(app, test_user, test_location):
    with app.app_context():
        checkins = [
            # Today
            CheckInModel(text='test',
                         lat=1.0,
                         lng=1.0,
                         final_distance=2.0,
                         user_id=test_user.id,
                         geocache_id=test_location,
                         created_at=date.today() - timedelta(days=0)),

            # Today
            CheckInModel(text='test',
                         lat=1.0,
                         lng=1.0,
                         final_distance=2.0,
                         user_id=test_user.id,
                         geocache_id=test_location,
                         created_at=date.today() - timedelta(days=0)),

            # Today
            CheckInModel(text='test',
                         lat=1.0,
                         lng=1.0,
                         final_distance=2.0,
                         user_id=test_user.id,
                         geocache_id=test_location,
                         created_at=date.today() - timedelta(days=0)),

            # Today
            CheckInModel(text='test',
                         lat=1.0,
                         lng=1.0,
                         final_distance=2.0,
                         user_id=test_user.id,
                         geocache_id=test_location,
                         created_at=date.today() - timedelta(days=0)),

            # 6 Days Ago
            CheckInModel(text='test',
                         lat=1.0,
                         lng=1.0,
                         final_distance=2.0,
                         user_id=test_user.id,
                         geocache_id=test_location,
                         created_at=date.today() - timedelta(days=6)),

            # 6 Days Ago
            CheckInModel(text='test',
                         lat=1.0,
                         lng=1.0,
                         final_distance=2.0,
                         user_id=test_user.id,
                         geocache_id=test_location,
                         created_at=date.today() - timedelta(days=6)),

            # 6 Days Ago
            CheckInModel(text='test',
                         lat=1.0,
                         lng=1.0,
                         final_distance=2.0,
                         user_id=test_user.id,
                         geocache_id=test_location,
                         created_at=date.today() - timedelta(days=6)),

            # 6 Days Ago
            CheckInModel(text='test',
                         lat=1.0,
                         lng=1.0,
                         final_distance=2.0,
                         user_id=test_user.id,
                         geocache_id=test_location,
                         created_at=date.today() - timedelta(days=6)),
        ]

        db.session.add_all(checkins)

        db.session.commit()

        return len(checkins)


def test_get_user_stats(app, client, test_user, current_streak, longest_streak):
    # hit the api
    rv = client.get(f'/stats/',
                    headers=test_user.auth_headers)

    assert rv.status_code == 200

    json_data = rv.get_json()

    validate_json(json_data, 'stats.response.json')

    with app.app_context():
        num_checkins = CheckInModel.query.filter_by(user_id=test_user.id).count()

        assert num_checkins == json_data['num_checkins']
        assert current_streak == json_data['current_streak']
        assert longest_streak == json_data['longest_streak']


@pytest.mark.usefixtures('multiple_checkins_one_day_current_streak')
def test_get_user_stats_multiple_checkins_one_day(app, client, test_user, current_streak, longest_streak):
    # ensure that multiple checkins on the same day do not increment the streak
    # hit the api
    rv = client.get(f'/stats/',
                    headers=test_user.auth_headers)

    assert rv.status_code == 200

    json_data = rv.get_json()

    validate_json(json_data, 'stats.response.json')

    with app.app_context():
        num_checkins = CheckInModel.query.filter_by(user_id=test_user.id).count()

        assert num_checkins == json_data['num_checkins']
        assert current_streak == json_data['current_streak']
        assert longest_streak == json_data['longest_streak']


def test_get_user_stats_no_checkins(app, client, test_user):
    # hit the api
    rv = client.get(f'/stats/',
                    headers=test_user.auth_headers)

    assert rv.status_code == 200

    json_data = rv.get_json()

    validate_json(json_data, 'stats.response.json')

    assert 0 == json_data['num_checkins']
    assert 0 == json_data['current_streak']
    assert 0 == json_data['longest_streak']
