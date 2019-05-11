import io
import pytest

from otbp.models import ImageModel

from tests.support.assertions import validate_json


@pytest.fixture
def test_photo(app, client, test_user):
    data = {
        'file': (io.BytesIO(b'abcdef'), 'test.jpg')
    }

    with app.app_context():
        # hit the api
        rv = client.post('/photo/',
                         data=data,
                         content_type='multipart/form-data',
                         headers=test_user.auth_headers)

        return rv.get_json()['id']


def test_upload_photo_without_credentials(app, client, test_user):
    data = {
        'file': (io.BytesIO(b'abcdef'), 'test.jpg')
    }

    # hit the api
    rv = client.post('/photo/',
                     data=data,
                     content_type='multipart/form-data')

    assert rv.status_code == 401

    assert 'JWT token not found' in rv.get_json()['message']


def test_upload_photo(app, client, test_user):
    data = {
        'file': (io.BytesIO(b'abcdef'), 'test.jpg')
    }

    with app.app_context():
        # hit the api
        rv = client.post('/photo/',
                         data=data,
                         content_type='multipart/form-data',
                         headers=test_user.auth_headers)

        assert rv.status_code == 201

        json_data = rv.get_json()

        # confirm login succeeded
        validate_json(json_data, 'photo.response.json')

        # confirm photo is created in database
        photo = ImageModel.query.filter_by(id=json_data['id']).first()

        assert photo is not None
        assert photo.user_id == test_user.id

        # confirm file created
        assert open(photo.filepath, 'r')


def test_get_photo(app, client, test_user, test_photo):
    with app.app_context():
        photo = ImageModel.query.get(test_photo)

        rv = client.get(f'/photo/{photo.filename}',
                        headers=test_user.auth_headers)

        assert rv.status_code == 200


def test_photo_doesnt_exist(app, client, test_user, test_photo):
    with app.app_context():
        rv = client.get(f'/photo/999999999.png',
                        headers=test_user.auth_headers)

        assert rv.status_code == 404


def test_get_photo_without_credentials(app, client, test_user, test_photo):
    with app.app_context():
        photo = ImageModel.query.get(test_photo)

        rv = client.get(f'/photo/{photo.filename}')

        assert rv.status_code == 401


def test_get_photo_with_other_user_credentials(app, client, test_photo, test_other_user):
    with app.app_context():
        photo = ImageModel.query.get(test_photo)

        rv = client.get(f'/photo/{photo.filename}',
                        headers=test_other_user.auth_headers)

        assert rv.status_code == 401
