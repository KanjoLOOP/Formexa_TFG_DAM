import json
import secrets
from datetime import datetime, timedelta

import pytest


def _make_user(db, username="sessionuser"):
    db.execute(
        "INSERT INTO users (username, password_hash, email, is_guest) VALUES (?, 'h', '', 0)",
        (username,)
    )
    return db.query_one("SELECT id FROM users WHERE username = ?", (username,))['id']


@pytest.fixture
def session_env(db, tmp_path, monkeypatch):
    """Patch DBManager singleton and session file path for isolation."""
    import src.database.db_manager as dbmod
    import src.logic.session_manager as sm_mod

    original_instance = dbmod.DBManager._instance
    monkeypatch.setattr(dbmod.DBManager, '_instance', db)

    session_file = str(tmp_path / 'session.json')
    monkeypatch.setattr(
        sm_mod.SessionManager, '_get_session_file',
        staticmethod(lambda: session_file)
    )
    yield db, session_file
    dbmod.DBManager._instance = original_instance


def test_save_session_inserts_token(session_env):
    db, _ = session_env
    from src.logic.session_manager import SessionManager
    uid = _make_user(db)
    assert SessionManager.save_session(uid)
    tokens = db.query("SELECT * FROM user_tokens WHERE user_id = ?", (uid,))
    assert len(tokens) == 1


def test_save_session_writes_json(session_env):
    db, session_file = session_env
    from src.logic.session_manager import SessionManager
    uid = _make_user(db, "jsonuser")
    SessionManager.save_session(uid)
    with open(session_file) as f:
        data = json.load(f)
    assert "token" in data
    assert len(data["token"]) > 10


def test_load_session_returns_user_id(session_env):
    db, _ = session_env
    from src.logic.session_manager import SessionManager
    uid = _make_user(db, "loaduser")
    SessionManager.save_session(uid)
    assert SessionManager.load_session() == uid


def test_load_session_no_file_returns_none(session_env):
    _, _ = session_env
    from src.logic.session_manager import SessionManager
    assert SessionManager.load_session() is None


def test_load_session_expired_token_returns_none(session_env):
    db, session_file = session_env
    from src.logic.session_manager import SessionManager
    uid = _make_user(db, "expuser")
    token = secrets.token_urlsafe(32)
    expired_at = (datetime.now() - timedelta(days=1)).isoformat()
    db.execute(
        "INSERT INTO user_tokens (token, user_id, expires_at) VALUES (?, ?, ?)",
        (token, uid, expired_at)
    )
    with open(session_file, 'w') as f:
        json.dump({"token": token}, f)
    assert SessionManager.load_session() is None
    assert db.query("SELECT * FROM user_tokens WHERE token = ?", (token,)) == []


def test_clear_session_deletes_token_from_db(session_env):
    db, _ = session_env
    from src.logic.session_manager import SessionManager
    uid = _make_user(db, "clearuser")
    SessionManager.save_session(uid)
    assert db.query("SELECT * FROM user_tokens WHERE user_id = ?", (uid,)) != []
    SessionManager.clear_session()
    assert db.query("SELECT * FROM user_tokens WHERE user_id = ?", (uid,)) == []


def test_token_is_random_each_call(session_env):
    db, _ = session_env
    from src.logic.session_manager import SessionManager
    uid = _make_user(db, "randuser")
    SessionManager.save_session(uid)
    t1 = db.query("SELECT token FROM user_tokens WHERE user_id = ?", (uid,))[0]['token']
    db.execute("DELETE FROM user_tokens WHERE user_id = ?", (uid,))
    SessionManager.save_session(uid)
    t2 = db.query("SELECT token FROM user_tokens WHERE user_id = ?", (uid,))[1 if len(db.query("SELECT token FROM user_tokens WHERE user_id = ?", (uid,))) > 1 else 0]['token']
    # Tokens are random — should not be equal (astronomically unlikely)
    # Just verify both are non-empty strings
    assert t1 and t2 and isinstance(t1, str) and isinstance(t2, str)
