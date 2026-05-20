import gc
import hashlib
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.db_manager import DBManager
from src.logic.auth_manager import AuthManager

SCHEMA_PATH = os.path.join(os.path.dirname(__file__), '..', 'src', 'database', 'schema.sql')


def _make_test_auth() -> tuple:
    """Return (AuthManager, DBManager) backed by a fresh temp DB."""
    tmp_fd, tmp_path = tempfile.mkstemp(suffix='.db')
    os.close(tmp_fd)

    db = DBManager(tmp_path)
    db.init_db(os.path.normpath(SCHEMA_PATH))

    # user_tokens may not be in schema yet on older installs — ensure it exists
    db.connect()
    db.connection.execute("""
        CREATE TABLE IF NOT EXISTS user_tokens (
            token TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    db.connection.commit()

    auth = AuthManager.__new__(AuthManager)
    auth.db = db
    auth.current_user = None
    from argon2 import PasswordHasher
    auth._ph = PasswordHasher()
    auth._failed_attempts = {}

    return auth, db, tmp_path


class TestAuthArgon2(unittest.TestCase):

    def setUp(self):
        self.auth, self.db, self.tmp_path = _make_test_auth()

    def tearDown(self):
        self.db.disconnect()
        self.auth.db = None
        gc.collect()
        try:
            os.unlink(self.tmp_path)
        except OSError:
            pass

    # ------------------------------------------------------------------
    # 1. New registration uses argon2id
    # ------------------------------------------------------------------
    def test_register_produces_argon2_hash(self):
        ok, _ = self.auth.register("alice01", "securepass", "")
        self.assertTrue(ok)
        row = self.db.query_one("SELECT password_hash FROM users WHERE username = ?", ("alice01",))
        self.assertIsNotNone(row)
        self.assertTrue(row['password_hash'].startswith("$argon2"), f"Expected argon2 hash, got: {row['password_hash']}")

    # ------------------------------------------------------------------
    # 2. Legacy SHA-256 login succeeds, hash is rehashed to argon2
    # ------------------------------------------------------------------
    def test_legacy_sha256_login_and_rehash(self):
        legacy_hash = hashlib.sha256("hunter2!!".encode()).hexdigest()
        self.db.execute(
            "INSERT INTO users (username, password_hash, email, is_guest) VALUES (?, ?, '', 0)",
            ("legacy_user", legacy_hash)
        )

        ok, msg = self.auth.login("legacy_user", "hunter2!!")
        self.assertTrue(ok, msg)

        row = self.db.query_one("SELECT password_hash FROM users WHERE username = ?", ("legacy_user",))
        self.assertTrue(row['password_hash'].startswith("$argon2"), "Legacy hash was not rehashed to argon2")

    # ------------------------------------------------------------------
    # 3. Salt+sha256 login succeeds, hash is rehashed to argon2
    # ------------------------------------------------------------------
    def test_salt_sha256_login_and_rehash(self):
        import os as _os
        salt = _os.urandom(16).hex()
        salted_hash = f"{salt}${hashlib.sha256((salt + 'mypassword1').encode()).hexdigest()}"
        self.db.execute(
            "INSERT INTO users (username, password_hash, email, is_guest) VALUES (?, ?, '', 0)",
            ("salted_user", salted_hash)
        )

        ok, msg = self.auth.login("salted_user", "mypassword1")
        self.assertTrue(ok, msg)

        row = self.db.query_one("SELECT password_hash FROM users WHERE username = ?", ("salted_user",))
        self.assertTrue(row['password_hash'].startswith("$argon2"), "Salt+sha hash was not rehashed to argon2")

    # ------------------------------------------------------------------
    # 4. Rate limiter blocks after 5 failed attempts
    # ------------------------------------------------------------------
    def test_rate_limit_blocks_after_five_failures(self):
        self.auth.register("bob01", "correctpass1", "")

        for i in range(5):
            ok, _ = self.auth.login("bob01", "wrongpassword")
            self.assertFalse(ok)

        ok, msg = self.auth.login("bob01", "correctpass1")
        self.assertFalse(ok)
        self.assertIn("minuto", msg.lower())

    # ------------------------------------------------------------------
    # 5. Input validation rejects short/bad usernames and passwords
    # ------------------------------------------------------------------
    def test_register_validation(self):
        ok, _ = self.auth.register("ab", "validpass1", "")
        self.assertFalse(ok, "Username too short should fail")

        ok, _ = self.auth.register("valid_user", "short", "")
        self.assertFalse(ok, "Short password should fail")

        ok, _ = self.auth.register("bad user!", "validpass1", "")
        self.assertFalse(ok, "Username with invalid chars should fail")


if __name__ == '__main__':
    unittest.main()
