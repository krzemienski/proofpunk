import pytest

from flaskr.db import get_db


def test_index(client, auth):
    response = client.get("/")
    assert b"Log In" in response.data
    assert b"Register" in response.data

    auth.login()
    response = client.get("/")
    assert b"test title" in response.data
    assert b"by test on 2018-01-01" in response.data
    assert b"test\nbody" in response.data
    assert b'href="/1/update"' in response.data


@pytest.mark.parametrize("path", ("/create", "/1/update", "/1/delete"))
def test_login_required(client, path):
    response = client.post(path)
    assert response.headers["Location"] == "/auth/login"


def test_author_required(app, client, auth):
    # change the post author to another user
    with app.app_context():
        db = get_db()
        db.execute("UPDATE post SET author_id = 2 WHERE id = 1")
        db.commit()

    auth.login()
    # current user can't modify other user's post
    assert client.post("/1/update").status_code == 403
    assert client.post("/1/delete").status_code == 403
    # current user doesn't see edit link
    assert b'href="/1/update"' not in client.get("/").data


@pytest.mark.parametrize("path", ("/2/update", "/2/delete"))
def test_exists_required(client, auth, path):
    auth.login()
    assert client.post(path).status_code == 404


def test_create(client, auth, app):
    auth.login()
    assert client.get("/create").status_code == 200
    client.post("/create", data={"title": "created", "body": ""})

    with app.app_context():
        db = get_db()
        count = db.execute("SELECT COUNT(id) FROM post").fetchone()[0]
        assert count == 2


def test_update(client, auth, app):
    auth.login()
    assert client.get("/1/update").status_code == 200
    client.post("/1/update", data={"title": "updated", "body": ""})

    with app.app_context():
        db = get_db()
        post = db.execute("SELECT * FROM post WHERE id = 1").fetchone()
        assert post["title"] == "updated"


@pytest.mark.parametrize("path", ("/create", "/1/update"))
def test_create_update_validate(client, auth, path):
    auth.login()
    response = client.post(path, data={"title": "", "body": ""})
    assert b"Title is required." in response.data


def test_delete(client, auth, app):
    auth.login()
    response = client.post("/1/delete")
    assert response.headers["Location"] == "/"

    with app.app_context():
        db = get_db()
        post = db.execute("SELECT * FROM post WHERE id = 1").fetchone()
        assert post is None


def test_create_stores_mood(client, auth, app):
    auth.login()
    client.post("/create", data={"title": "moody", "body": "b", "mood": "🔥"})

    with app.app_context():
        post = get_db().execute("SELECT * FROM post WHERE title = 'moody'").fetchone()
        assert post["mood"] == "🔥"


def test_create_invalid_mood_defaults(client, auth, app):
    auth.login()
    client.post(
        "/create",
        data={"title": "forged", "body": "b", "mood": "<script>alert(1)</script>"},
    )

    with app.app_context():
        post = get_db().execute("SELECT * FROM post WHERE title = 'forged'").fetchone()
        assert post["mood"] == "😐"


def test_update_changes_mood(client, auth, app):
    auth.login()
    client.post("/1/update", data={"title": "test title", "body": "b", "mood": "😢"})

    with app.app_context():
        post = get_db().execute("SELECT * FROM post WHERE id = 1").fetchone()
        assert post["mood"] == "😢"


def test_missing_mood_defaults(client, auth, app):
    # baseline behavior: forms without a mood field must not break (G-05)
    auth.login()
    client.post("/create", data={"title": "plain", "body": "b"})

    with app.app_context():
        post = get_db().execute("SELECT * FROM post WHERE title = 'plain'").fetchone()
        assert post["mood"] == "😐"


def test_index_shows_mood(client, auth):
    auth.login()
    response = client.get("/")
    # fixture post defaults to 😐 and renders it beside the title
    assert "😐".encode() in response.data


def test_index_filter_by_mood(client, auth):
    auth.login()
    client.post("/create", data={"title": "sadpost", "body": "b", "mood": "😢"})

    response = client.get("/?mood=😢")
    assert b"sadpost" in response.data
    assert b"test title" not in response.data  # fixture post is 😐

    response = client.get("/")
    assert b"sadpost" in response.data
    assert b"test title" in response.data


def test_index_invalid_mood_param_ignored(client, auth):
    auth.login()
    response = client.get("/?mood=🦄")
    assert response.status_code == 200
    assert b"test title" in response.data  # unfiltered


def test_invalid_mood_flash(client, auth):
    auth.login()
    response = client.post(
        "/create",
        data={"title": "x", "body": "b", "mood": "bogus"},
        follow_redirects=True,
    )
    assert "Mood not recognized".encode() in response.data
