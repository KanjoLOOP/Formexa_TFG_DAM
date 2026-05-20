import pytest
from src.database.migrations import run_migrations, MIGRATIONS


def test_all_migration_versions_applied(db):
    rows = db.query("SELECT version FROM schema_version ORDER BY version")
    applied = {r['version'] for r in rows}
    assert set(MIGRATIONS.keys()) == applied


def test_migrations_idempotent(db):
    run_migrations(db)  # second run — should be no-op
    rows = db.query("SELECT version FROM schema_version")
    versions = [r['version'] for r in rows]
    assert len(versions) == len(set(versions))  # no duplicates


def test_schema_version_table_exists(db):
    result = db.query("SELECT name FROM sqlite_master WHERE type='table' AND name='schema_version'")
    assert len(result) == 1


def test_user_tokens_table_exists(db):
    result = db.query("SELECT name FROM sqlite_master WHERE type='table' AND name='user_tokens'")
    assert len(result) == 1


def test_customers_table_exists(db):
    result = db.query("SELECT name FROM sqlite_master WHERE type='table' AND name='customers'")
    assert len(result) == 1


def test_orders_table_exists(db):
    result = db.query("SELECT name FROM sqlite_master WHERE type='table' AND name='orders'")
    assert len(result) == 1


def test_indexes_created(db):
    indexes = {r['name'] for r in db.query("SELECT name FROM sqlite_master WHERE type='index'")}
    expected = {
        'idx_filaments_user', 'idx_models_user', 'idx_projects_user',
        'idx_projects_status', 'idx_projects_user_status', 'idx_user_tokens_user',
        'idx_orders_customer', 'idx_orders_status', 'idx_customers_user',
    }
    assert expected.issubset(indexes)


def test_fresh_db_migration_from_zero():
    from src.database.db_manager import DBManager
    import os
    schema = os.path.normpath(
        os.path.join(os.path.dirname(__file__), '..', 'src', 'database', 'schema.sql')
    )
    fresh = DBManager(db_file=":memory:")
    fresh.init_db(schema)
    run_migrations(fresh)
    current = fresh.query_one("SELECT MAX(version) AS v FROM schema_version")
    assert current['v'] == max(MIGRATIONS.keys())
    fresh.disconnect()
