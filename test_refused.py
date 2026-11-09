import uuid


# Registering the same user name twice is refused with its error message.
def test_duplicate_username_is_refused(api):
    user = {"username": "lab-" + uuid.uuid4().hex[:12], "password": "Pizza-2026"}
    res = api.post("/api/users", json=user)
    assert res.status_code == 201
    res = api.post("/api/users", json=user)
    assert res.status_code == 400
    assert res.json() == {"error": "username already taken"}


# A new user cannot log in with a wrong password.
def test_wrong_password_is_refused(api):
    user = {"username": "lab-" + uuid.uuid4().hex[:12], "password": "Pizza-2026"}
    res = api.post("/api/users", json=user)
    assert res.status_code == 201
    res = api.post("/api/users/token/login", json={**user, "password": "Wrong-2026"})
    assert res.status_code == 401
    assert res.json() == {"error": "authentication failed"}


# Registration with an empty user name is refused with its error message.
def test_empty_username_is_refused(api):
    res = api.post("/api/users", json={"username": "", "password": "Pizza-2026"})
    assert res.status_code == 400
    assert res.json() == {"error": "username field is empty"}
