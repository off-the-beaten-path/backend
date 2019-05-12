def test_get_geocache(app, client, test_user):
    # hit the api
    rv = client.get('/geocache/42.38,-83.84',
                    headers=test_user.auth_headers)

    assert rv.status_code == 200
