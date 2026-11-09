import pytest


# Update boundaries save 1 and 5; refusing 0 or 6 leaves the original stars intact.
@pytest.mark.parametrize("stars, expected_status", [(0, 400), (1, 200), (5, 200), (6, 400)])
def test_update_star_boundaries(api, auth, rating, stars, expected_status):
    path = f"/api/ratings/{rating['id']}"
    res = api.put(path, json={"stars": stars}, headers=auth)
    assert res.status_code == expected_status
    expected_stars = stars if expected_status == 200 else rating["stars"]
    if expected_status == 200:
        assert res.json()["stars"] == stars
    else:
        assert res.json() == {"error": "number of stars must be between 1 and 5 (inclusive)"}
    saved = api.get(path, headers=auth)
    assert saved.status_code == 200
    assert saved.json()["stars"] == expected_stars
