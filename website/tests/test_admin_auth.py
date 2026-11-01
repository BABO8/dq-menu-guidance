import pytest
from starlette.testclient import TestClient
from app.main import app
from app.auth import hash_password, verify_password, create_admin_session, clear_failed_logins
from app.config import settings

@pytest.fixture
def client():
    # Clear any rate limit state before test
    clear_failed_logins("testclient")
    clear_failed_logins("127.0.0.1")
    return TestClient(app)

def test_password_hashing():
    pw = "SuperSecurePassword123!"
    hashed = hash_password(pw)
    assert hashed.startswith(("$2b$", "$2a$", "$2y$"))
    assert verify_password(pw, hashed) is True
    assert verify_password("WrongPassword!", hashed) is False

    # Test legacy PBKDF2 hash verification compatibility
    legacy_hash = "pbkdf2:sha256:600000$51893b8b2ba02cbe$4ff6455565810b60e1028e8e26617c7d4c7cdce63aee1c2a4ba9782b46868e24"
    assert verify_password("DqPriceGuide2026!Admin", legacy_hash) is True

def test_admin_login_success(client):
    # 1. GET login page receives CSRF cookie
    res_get = client.get("/admin/login")
    assert res_get.status_code == 200
    assert "Editorial Dashboard" in res_get.text or "Sign In" in res_get.text
    assert settings.CSRF_COOKIE_NAME in res_get.cookies

    # 2. Extract CSRF token from form
    csrf_token = res_get.text.split('name="csrf_token" value="')[1].split('"')[0]

    # 3. Successful login
    res_post = client.post("/admin/login", data={
        "csrf_token": csrf_token,
        "username": "editorial_admin",
        "password": "DqPriceGuide2026!Admin"
    }, follow_redirects=False)

    assert res_post.status_code == 303
    assert res_post.headers["location"] == "/admin/dashboard"
    assert settings.SESSION_COOKIE_NAME in res_post.cookies

    # 4. Access dashboard with the session cookie on client
    client.cookies[settings.SESSION_COOKIE_NAME] = res_post.cookies[settings.SESSION_COOKIE_NAME]
    res_dash = client.get("/admin/dashboard")
    assert res_dash.status_code == 200
    assert "Editorial Control Center" in res_dash.text or "Content Management Overview" in res_dash.text
    assert "Published Articles" in res_dash.text

def test_admin_login_invalid_password_rejected(client):
    res_get = client.get("/admin/login")
    csrf_token = res_get.text.split('name="csrf_token" value="')[1].split('"')[0]

    res_bad = client.post("/admin/login", data={
        "csrf_token": csrf_token,
        "username": "editorial_admin",
        "password": "IncorrectPasswordAttempt!"
    })
    assert res_bad.status_code == 401
    assert "Invalid username or password" in res_bad.text

def test_admin_login_brute_force_throttling(client):
    res_get = client.get("/admin/login")
    csrf_token = res_get.text.split('name="csrf_token" value="')[1].split('"')[0]

    # Trigger failed attempts up to limit
    for _ in range(settings.LOGIN_MAX_FAILED_ATTEMPTS):
        res = client.post("/admin/login", data={
            "csrf_token": csrf_token,
            "username": "editorial_admin",
            "password": "WrongPasswordAttempt"
        })
        assert res.status_code == 401

    # Next attempt must be throttled with 429
    res_blocked = client.post("/admin/login", data={
        "csrf_token": csrf_token,
        "username": "editorial_admin",
        "password": "WrongPasswordAttempt"
    })
    assert res_blocked.status_code == 429
    assert "Too many failed login attempts" in res_blocked.text

def test_admin_logout_clears_session(client):
    # 1. Login
    res_get = client.get("/admin/login")
    csrf_token = res_get.text.split('name="csrf_token" value="')[1].split('"')[0]
    res_login = client.post("/admin/login", data={
        "csrf_token": csrf_token,
        "username": "editorial_admin",
        "password": "DqPriceGuide2026!Admin"
    }, follow_redirects=False)

    client.cookies[settings.SESSION_COOKIE_NAME] = res_login.cookies[settings.SESSION_COOKIE_NAME]

    # 2. Logout
    res_logout = client.get("/admin/logout", follow_redirects=False)
    assert res_logout.status_code == 303
    assert res_logout.headers["location"] == "/admin/login"

def test_unauthorized_post_rejected(client):
    # Attempting to delete an article without being logged in should redirect to login
    res = client.post("/admin/articles/delete/1", data={"csrf_token": "none"}, follow_redirects=False)
    assert res.status_code == 303
    assert res.headers.get("location") == "/admin/login"

def test_unauthorized_menu_item_create_rejected(client):
    # Attempting to add a menu item without admin session
    res = client.post("/admin/menu-items/new", data={
        "name": "Hacked Burger",
        "csrf_token": "fake"
    }, follow_redirects=False)
    assert res.status_code == 303
    assert res.headers.get("location") == "/admin/login"

def test_admin_csrf_protection_rejects_missing_or_invalid_token(client):
    # Valid session but invalid CSRF token
    token = create_admin_session("editorial_admin")
    client.cookies[settings.SESSION_COOKIE_NAME] = token
    res = client.post("/admin/menu-items/new", data={
        "name": "Hacked Burger",
        "csrf_token": "invalid_forged_csrf_token"
    })
    assert res.status_code == 400
    assert "Invalid CSRF token" in res.text
