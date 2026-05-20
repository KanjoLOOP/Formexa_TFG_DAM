import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.db_manager import DBManager
from src.database.migrations import run_migrations

SCHEMA = os.path.normpath(
    os.path.join(os.path.dirname(__file__), '..', 'src', 'database', 'schema.sql')
)


@pytest.fixture
def db():
    instance = DBManager(db_file=":memory:")
    instance.init_db(SCHEMA)
    run_migrations(instance)
    yield instance
    instance.disconnect()


@pytest.fixture
def auth(db):
    from src.logic.auth_manager import AuthManager
    from argon2 import PasswordHasher
    a = AuthManager.__new__(AuthManager)
    a.db = db
    a.current_user = None
    a._ph = PasswordHasher()
    a._failed_attempts = {}
    return a
