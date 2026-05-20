import pytest


def test_query_returns_list_of_dicts(db):
    result = db.query("SELECT 1 AS x, 2 AS y")
    assert result == [{'x': 1, 'y': 2}]


def test_query_empty_returns_empty_list(db):
    result = db.query("SELECT * FROM users WHERE id = 99999")
    assert result == []


def test_query_one_returns_dict(db):
    result = db.query_one("SELECT 42 AS n")
    assert result == {'n': 42}


def test_query_one_returns_none_for_empty(db):
    result = db.query_one("SELECT * FROM users WHERE id = 99999")
    assert result is None


def test_execute_returns_lastrowid(db):
    row_id = db.execute(
        "INSERT INTO users (username, password_hash, email, is_guest) VALUES ('u1','h','',0)"
    )
    assert isinstance(row_id, int)
    assert row_id > 0


def test_executemany_inserts_all_rows(db):
    rows = [('em1', 'h', '', 0), ('em2', 'h', '', 0)]
    db.executemany(
        "INSERT INTO users (username, password_hash, email, is_guest) VALUES (?, ?, ?, ?)",
        rows
    )
    count = db.query_one("SELECT COUNT(*) AS n FROM users WHERE username IN ('em1','em2')")
    assert count['n'] == 2


def test_transaction_commit_persists(db):
    with db.transaction():
        db.execute("INSERT INTO users (username, password_hash, email, is_guest) VALUES ('tx1','h','',0)")
    row = db.query_one("SELECT * FROM users WHERE username = 'tx1'")
    assert row is not None


def test_transaction_rollback_on_exception(db):
    with pytest.raises(RuntimeError):
        with db.transaction():
            db.execute("INSERT INTO users (username, password_hash, email, is_guest) VALUES ('rb1','h','',0)")
            raise RuntimeError("force rollback")
    row = db.query_one("SELECT * FROM users WHERE username = 'rb1'")
    assert row is None


def test_multiple_queries_same_connection(db):
    db.execute("INSERT INTO users (username, password_hash, email, is_guest) VALUES ('mq1','h','',0)")
    db.execute("INSERT INTO users (username, password_hash, email, is_guest) VALUES ('mq2','h','',0)")
    result = db.query("SELECT username FROM users WHERE username LIKE 'mq%' ORDER BY username")
    assert [r['username'] for r in result] == ['mq1', 'mq2']
