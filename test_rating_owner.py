# Another user cannot read a rating, and its owner's copy remains unchanged.
def test_other_user_cannot_read_rating(api, auth, other_auth, rating):
    path = f"/api/ratings/{rating['id']}"
    res = api.get(path, headers=other_auth)
    print(f"Other-user GET status: {res.status_code}")
    assert 400 <= res.status_code <= 499
    saved = api.get(path, headers=auth)
    assert saved.status_code == 200
    assert saved.json() == rating


# Another user cannot change a rating, and its owner's copy remains unchanged.
def test_other_user_cannot_update_rating(api, auth, other_auth, rating):
    path = f"/api/ratings/{rating['id']}"
    res = api.put(path, json={"stars": 5}, headers=other_auth)
    print(f"Other-user PUT status: {res.status_code}")
    assert 400 <= res.status_code <= 499
    saved = api.get(path, headers=auth)
    assert saved.status_code == 200
    assert saved.json() == rating


# Another user cannot delete a rating, and its owner's copy remains unchanged.
def test_other_user_cannot_delete_rating(api, auth, other_auth, rating):
    path = f"/api/ratings/{rating['id']}"
    res = api.delete(path, headers=other_auth)
    print(f"Other-user DELETE status: {res.status_code}")
    assert 400 <= res.status_code <= 499
    saved = api.get(path, headers=auth)
    assert saved.status_code == 200
    assert saved.json() == rating
