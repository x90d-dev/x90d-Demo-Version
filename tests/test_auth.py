from app import app
from modules.database import init_db


def test_training_requires_admin_login(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "auth.db"))
    init_db()

    app.config.update(TESTING=True, WTF_CSRF_ENABLED=False)
    with app.test_client() as client:
        response = client.get("/training")

    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_default_admin_can_login_and_see_training(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "auth.db"))
    init_db()

    app.config.update(TESTING=True, WTF_CSRF_ENABLED=False)
    with app.test_client() as client:
        login_response = client.post(
            "/login",
            data={"login": "dhafir", "password": "dhafir012"},
            follow_redirects=True,
        )
        training_response = client.get("/training")

    assert login_response.status_code == 200
    assert training_response.status_code == 200
    assert b"Training" in training_response.data


def test_training_menu_hidden_for_guest_and_visible_for_admin(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "auth.db"))
    init_db()

    app.config.update(TESTING=True, WTF_CSRF_ENABLED=False)
    with app.test_client() as client:
        guest_response = client.get("/chat")
        client.post("/login", data={"login": "dhafir", "password": "dhafir012"})
        admin_response = client.get("/chat")

    assert b">Training<" not in guest_response.data
    assert b">Training<" in admin_response.data
    assert b"Admin" in admin_response.data


def test_regular_user_display_name_uses_username(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "auth.db"))
    init_db()

    app.config.update(TESTING=True, WTF_CSRF_ENABLED=False)
    with app.test_client() as client:
        client.post("/register", data={"username": "budi", "email": "budi@local", "password": "secret123"})
        client.post("/login", data={"login": "budi", "password": "secret123"})
        response = client.get("/chat")

    assert b"budi" in response.data
    assert b">Training<" not in response.data
