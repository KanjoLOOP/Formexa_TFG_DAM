import hashlib
import os

import pytest


# ── register / login ──────────────────────────────────────────────────────────

def test_register_produces_argon2_hash(db, auth):
    ok, _ = auth.register("alice01", "securepass1", "")
    assert ok
    row = db.query_one("SELECT password_hash FROM users WHERE username = ?", ("alice01",))
    assert row["password_hash"].startswith("$argon2")


def test_login_success(auth):
    auth.register("bob01", "securepass1", "")
    ok, _ = auth.login("bob01", "securepass1")
    assert ok
    assert auth.current_user is not None
    assert auth.current_user["username"] == "bob01"


def test_login_wrong_password(auth):
    auth.register("charlie", "correctpass1", "")
    ok, _ = auth.login("charlie", "wrongpass")
    assert not ok


def test_login_unknown_user(auth):
    ok, _ = auth.login("nobody", "pass12345")
    assert not ok


def test_login_sets_current_user(auth):
    auth.register("dora01", "securepass1", "")
    auth.login("dora01", "securepass1")
    assert auth.current_user["username"] == "dora01"
    assert auth.current_user["is_guest"] == 0


# ── legacy hash compatibility ─────────────────────────────────────────────────

def test_legacy_sha256_login_rehash(db, auth):
    legacy = hashlib.sha256("hunter2!!".encode()).hexdigest()
    db.execute(
        "INSERT INTO users (username, password_hash, email, is_guest) VALUES (?, ?, '', 0)",
        ("legacy", legacy)
    )
    ok, _ = auth.login("legacy", "hunter2!!")
    assert ok
    row = db.query_one("SELECT password_hash FROM users WHERE username = ?", ("legacy",))
    assert row["password_hash"].startswith("$argon2")


def test_salt_sha256_login_rehash(db, auth):
    salt = os.urandom(16).hex()
    salted = f"{salt}${hashlib.sha256((salt + 'mypassword1').encode()).hexdigest()}"
    db.execute(
        "INSERT INTO users (username, password_hash, email, is_guest) VALUES (?, ?, '', 0)",
        ("salted", salted)
    )
    ok, _ = auth.login("salted", "mypassword1")
    assert ok
    row = db.query_one("SELECT password_hash FROM users WHERE username = ?", ("salted",))
    assert row["password_hash"].startswith("$argon2")


# ── rate limiting ─────────────────────────────────────────────────────────────

def test_rate_limit_after_five_failures(auth):
    auth.register("victim", "correctpass1", "")
    for _ in range(5):
        auth.login("victim", "wrongpass")
    ok, msg = auth.login("victim", "correctpass1")
    assert not ok
    assert "minuto" in msg.lower()


def test_rate_limit_resets_on_success(auth):
    auth.register("resilient", "correctpass1", "")
    for _ in range(3):
        auth.login("resilient", "wrongpass")
    ok, _ = auth.login("resilient", "correctpass1")
    assert ok


# ── input validation ──────────────────────────────────────────────────────────

def test_register_username_too_short(auth):
    ok, _ = auth.register("ab", "validpass1", "")
    assert not ok


def test_register_password_too_short(auth):
    ok, _ = auth.register("valid_user", "short", "")
    assert not ok


def test_register_username_invalid_chars(auth):
    ok, _ = auth.register("bad user!", "validpass1", "")
    assert not ok


def test_register_duplicate_username(auth):
    auth.register("dupuser", "validpass1", "")
    ok, _ = auth.register("dupuser", "validpass1", "")
    assert not ok
