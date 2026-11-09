# API lab results

Recorded on 9 November 2026 against https://quickpizza.grafana.com.

Full run: `pytest -v --html=report.html --self-contained-html`

**32 passed, 1 xfailed in 36.06 seconds.** The expected failure is Defect 1 below. The delete test also passed when run alone with `pytest -v test_ratings.py::test_delete_rating` (1 passed in 4.37 seconds).

The HTML report was generated and its embedded results were checked. The test login token in the expected-failure traceback was redacted; test outcomes and assertion details were preserved. Visual review in a browser could not be completed because the available browser blocked opening the local report file.

## Part 0

- Step 0.1, the number of pizza names: **18**.
- Step 0.2: status **200**, `content-type: application/json`, and an `AWSALB` cookie were present.
- Step 0.3, status code of the request without a token: **401**, with `{"error":"authentication failed"}`.
- Step 0.4, the name of your pizza: **The Green Americana**. Its ingredients all had `vegetarian: true`.
- Step 0.12, results of the three runs without a session (optional): **Skipped**. No results are claimed for this optional experiment.
- Step 0.16, blocks of "how many of the three tools are excluded":

| Block | Example input | Expected result | Coverage |
| --- | --- | --- | --- |
| Zero tools excluded | `[]` | 200, returned tool is allowed | Added passing case |
| One tool excluded | `["Knife"]` or `["Scissors"]` | 200, returned tool is not excluded | Both original cases |
| Two tools excluded | `["Knife", "Scissors"]` | 200, remaining tool is used | Added passing case |
| Three tools excluded | `["Knife", "Pizza cutter", "Scissors"]` | 400 and a JSON error message | Separate strict xfail test |

The original two cases both covered only the one-tool block. Adding representatives for zero, two and three tools exposed the defect in the three-tool block. Curl independently confirmed status 500 and an empty response body for that request.

## Defect report

- **Title:** Excluding all three pizza tools returns an internal server error instead of a validation error.
- **Request:** `POST https://quickpizza.grafana.com/api/pizza`, using `Authorization: token <token obtained by logging in a newly created test user>` and `Content-Type: application/json`. Body:

  ```json
  {"excludedTools": ["Knife", "Pizza cutter", "Scissors"]}
  ```

  The body is saved in `excluded_all.json`. Curl sent this body from the file using the same session cookies and the test user's own login token.
- **Expected result:** HTTP **400** with a JSON error message explaining that no pizza can satisfy the restrictions, as specified by the product owner in Step 0.16.
- **Actual result:** HTTP **500** with an **empty body**, confirmed with curl and reproduced by `test_excluding_all_tools_is_refused`.
- **Severity:** **Medium**. This input is an ordinary customer restriction, but it causes an internal error and gives the calling app no explanation. Other tested operations still work; no wider outage was established.
- **Test treatment:** `@pytest.mark.xfail(reason="Defect 1: excluding all three tools returns 500 with an empty body instead of 400 and a JSON error message", strict=True)`. The test still asserts 400 and a nonempty JSON error message; it does not accept 500 as correct.

## Part A

The Step A1 input domain model and the test covering each block are in `README.md`. `test_create_rating.py` contains the nine base choice cases. The error responses for the non-base C2, C3 and C4 cases were obtained with curl before being used in assertions:

| Input | Status | Error message |
| --- | --- | --- |
| Decimal stars `3.5` | 400 | `json: cannot unmarshal number 3.5 into Go struct field Rating.stars of type int` |
| Text stars `"3"` | 400 | `json: cannot unmarshal string into Go struct field Rating.stars of type int` |
| Missing `stars` field | 400 | `number of stars must be between 1 and 5 (inclusive)` |
| Nonexistent pizza `999999999` | 400 | `pizza ID 999999999 not found` |
| No token | 401 | `authentication failed` |
| Wrong-length token `short` | 401 | `authentication failed` |

Step A3: updates to **1** and **5** returned **200**, and reading the rating back confirmed the new stars. Updates to **0** and **6** returned **400**, and reading the rating back confirmed that its original **3** stars were unchanged.

Step A4, status codes when the other user reads, changes and deletes:

| Other user's operation | Actual status | Owner's subsequent read |
| --- | --- | --- |
| Read (`GET`) | **404** | 200; the whole rating was unchanged |
| Change (`PUT`) | **400** | 200; the whole rating was unchanged |
| Delete (`DELETE`) | **400** | 200; the whole rating was unchanged |

The exact status codes are also captured in the ownership tests' output inside `report.html`.

## Part B

1. API tests can find failures in how the server and its data storage work together, such as a rating being reported as saved but not being available on a later read. They can also find authentication or load-balancer integration failures, such as a newly created user's login reaching a different server that does not know that user. A unit test with stubbed dependencies would not exercise those real connections. Unit tests with stubs are still useful because they run quickly and predictably and can isolate a particular function or simulate a rare dependency failure.

2. Each test creates a new made-up user so its ratings belong only to that test. The public token represents shared practice data, so another student's changes could interfere with a test or our tests could damage their data. In Project 2, use the group's permitted credentials, create uniquely named test records, keep their IDs, and update or delete only those records. Do not modify the shop's or hotel's existing records or another group's data.

3. A session remembers cookies returned by the server. QuickPizza's AWSALB cookie keeps requests on the same backend, where that backend stores the users. Without the cookie, registering a user and then logging in could reach different backends, so the login could fail even with the correct password. The shared `api` fixture keeps one session for the tests that need their own users and ratings. The early guided public-read and vegetarian tests keep the direct requests shown in the lab. I skipped optional Step 0.12, so there are no three-run observations to report.

4. The block excluding **all three tools** revealed the defect. No available tool can satisfy that request. A 400 response with a JSON message lets an app explain the invalid restrictions and ask the customer to change them. A 500 suggests a server failure, and an empty body gives no explanation and can also break a client that expects JSON. Keeping the test as a strict xfail records the intended behavior and keeps the known problem visible without making every run fail. If the test unexpectedly passes after a fix, strict mode makes the run fail so the mark can be removed.

5. Base choice needs **9 tests**: one base test plus one for each non-base block, `1 + (3 - 1) + (4 - 1) + (2 - 1) + (3 - 1) = 9`. All combinations of the model's blocks would need `3 × 4 × 2 × 3 = 72` combinations.

6. The actual codes were **404 for reading**, **400 for changing**, and **400 for deleting** another user's rating. I would normally expect **403 Forbidden** for an authenticated user who lacks permission. A 404 can also deliberately hide whether another user's resource exists. The 400 responses are less specific than 403, but all three operations were refused and the owner's subsequent read showed the whole rating was unchanged. Under the lab's stated requirement of any 400-499 status, this difference is not a demonstrated functional defect. If the API contract specifically promised 403, the mismatch would be a contract defect.

7. With `madeup.txt` containing `Authorization: token 0000000000000000`, the command `curl -H "@madeup.txt" https://quickpizza.grafana.com/api/ratings` returned **200** and a JSON object containing a **nonempty `ratings` list**, instead of rejecting the made-up token. The response included rating objects with `id`, `stars` and `pizza_id`. This indicates an authentication defect because an arbitrary token that was not obtained by logging in was accepted for the read. On a real system, a stranger could read data without legitimate credentials. Other unauthorized actions might be possible if the same validation is used for writes, but that was not tested. Only the read request was sent with this token; no data was created, changed or deleted with it.

8. An API test directly checks exact HTTP status codes and JSON response fields, including malformed inputs that a web form might prevent a user from entering. A test through the web pages can check whether a button works and whether the returned rating or error message is actually displayed correctly to the user; an API-only test cannot see the rendered page.
