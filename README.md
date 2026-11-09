# API lab: QuickPizza

ITCS386 Software Verification and Validation - API Testing with pytest and requests, Version 2.0.

This repository covers Part 0, Part A and Part B of the lab. `RESULTS.md` contains the observed results, defect report and reflection answers. `report.html` is the self-contained HTML report of a full run against https://quickpizza.grafana.com. Optional Step 0.12 was skipped.

## Install and run

Use Python 3.10 or newer, Git, curl and an editor with a terminal. Run the following commands from the repository folder.

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pytest -v
```

If PowerShell refuses activation, run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` once, then activate again, as described in the lab.

macOS or Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest -v
```

Generate the HTML report and open `report.html` in a browser:

```text
pytest -v --html=report.html --self-contained-html
```

Check that the delete test also passes independently:

```text
pytest -v test_ratings.py::test_delete_rating
```

The intended full-suite outcome is **32 passed, 1 xfailed** while Defect 1 exists. Its strict xfail becomes a failed run if the API fixes the defect, prompting removal of the mark. Read `RESULTS.md` for the actual recorded outcome.

## Input domain model: POST /api/ratings

Base choice: stars `3` as a whole number, a pizza obtained by the test, and that test user's login token.

| Characteristic | Block | Test value | Test covering the block |
| --- | --- | --- | --- |
| C1 Value of stars | Below 1 | `0` | `test_stars_out_of_range[0]` |
| C1 Value of stars | 1 to 5 (base) | `3` | `test_base_choice_is_saved` |
| C1 Value of stars | Above 5 | `6` | `test_stars_out_of_range[6]` |
| C2 Type of stars | Whole number (base) | `3` | `test_base_choice_is_saved` |
| C2 Type of stars | Decimal | `3.5` | `test_decimal_stars_are_refused` |
| C2 Type of stars | Text | `"3"` | `test_text_stars_are_refused` |
| C2 Type of stars | Missing | No `stars` field | `test_missing_stars_are_refused` |
| C3 Pizza | Exists (base) | ID returned by `pizza_id` | `test_base_choice_is_saved` |
| C3 Pizza | Does not exist | `999999999` | `test_nonexistent_pizza_is_refused` |
| C4 Token | User's own (base) | Token obtained by `auth` | `test_base_choice_is_saved` |
| C4 Token | None | No Authorization header | `test_missing_token_is_refused` |
| C4 Token | Wrong length | `token short` | `test_wrong_length_token_is_refused` |

Each non-base case changes one characteristic and keeps the others at base. The nine cases are in `test_create_rating.py`: one base, two C1 alternatives, three C2 alternatives, one C3 alternative and two C4 alternatives. Error messages were checked with curl before being asserted in these tests.

## Other test files

| File | Goal |
| --- | --- |
| `test_names.py` | Read names and check Margherita is present |
| `test_tools.py` | Read the three tools with the practice token |
| `test_pizza.py` | Check vegetarian ingredients and refusal without a token |
| `test_users.py` | Verify a fresh user starts with no ratings |
| `test_ratings.py` | Create, read, update and delete ratings |
| `test_refused.py` | Refuse duplicate names, wrong passwords and empty names |
| `test_excluded_tools.py` | Cover excluding zero, one, two and all three tools |
| `test_update_rating.py` | Test update boundaries 0, 1, 5 and 6 and read back the result |
| `test_rating_owner.py` | Refuse another user's read, update and delete attempts |

## Shared-site rules and fixtures

The session-scoped `api` fixture keeps the load-balancer cookies. Each test needing private data logs in a new made-up user. `other_auth` creates a second user for ownership tests. The `rating` fixture removes its rating during teardown; direct successful create tests remove their own ratings in `finally` blocks. Tests never change or delete another user's data.

`auth.txt` holds only the public practice token, used for the guided tools and pizza requests. It is never used to create or change ratings. `madeup.txt` is used only for the Part B read request. No real credentials or private login tokens are included.

The JSON files contain the request bodies used for curl. IDs in the recorded rating request bodies belong to that run; obtain a fresh pizza ID and your own login token before repeating those requests. On Windows PowerShell, use `curl.exe` wherever the lab says `curl`.
