import pytest


# Excluding zero, one or two tools still returns a pizza using an allowed tool.
@pytest.mark.parametrize("excluded", [[], ["Knife"], ["Scissors"], ["Knife", "Scissors"]])
def test_excluded_tool_is_not_used(api, auth, excluded):
    body = {"excludedTools": excluded}
    res = api.post("/api/pizza", json=body, headers=auth)
    assert res.status_code == 200
    assert res.json()["pizza"]["tool"] not in excluded


# Excluding all three tools must give a client error with a JSON error message.
@pytest.mark.xfail(
    reason="Defect 1: excluding all three tools returns 500 with an empty body instead of 400 and a JSON error message",
    strict=True,
)
def test_excluding_all_tools_is_refused(api, auth):
    body = {"excludedTools": ["Knife", "Pizza cutter", "Scissors"]}
    res = api.post("/api/pizza", json=body, headers=auth)
    assert res.status_code == 400
    data = res.json()
    assert isinstance(data["error"], str)
    assert data["error"] != ""
