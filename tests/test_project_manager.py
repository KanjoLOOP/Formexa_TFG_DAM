import pytest
from src.logic.project_manager import ProjectManager


def _setup(db, username="pmuser"):
    db.execute(
        "INSERT INTO users (username, password_hash, email, is_guest) VALUES (?, 'h', '', 0)",
        (username,)
    )
    uid = db.query_one("SELECT id FROM users WHERE username = ?", (username,))['id']
    db.execute(
        """INSERT INTO filaments
           (brand, material_type, color, weight_initial, weight_current, price, user_id)
           VALUES ('A','PLA','Black',1000,500,20.0,?)""",
        (uid,)
    )
    fid = db.query_one("SELECT id FROM filaments WHERE user_id = ?", (uid,))['id']
    return uid, fid


@pytest.fixture
def pm(db):
    manager = ProjectManager.__new__(ProjectManager)
    manager.db = db
    return manager


def test_create_project(db, pm):
    uid, _ = _setup(db)
    ok, _ = pm.create_project(uid, "Test Project")
    assert ok
    projects = pm.get_all_projects(uid)
    assert len(projects) == 1
    assert projects[0]['name'] == "Test Project"


def test_update_project(db, pm):
    uid, _ = _setup(db, "upuser")
    pm.create_project(uid, "Old Name")
    pid = pm.get_all_projects(uid)[0]['id']
    pm.update_project(pid, name="New Name")
    updated = pm.get_project_by_id(pid)
    assert updated['name'] == "New Name"


def test_delete_project(db, pm):
    uid, _ = _setup(db, "deluser")
    pm.create_project(uid, "To Delete")
    pid = pm.get_all_projects(uid)[0]['id']
    ok, _ = pm.delete_project(pid)
    assert ok
    assert pm.get_all_projects(uid) == []


def test_mark_as_completed_deducts_stock(db, pm):
    uid, fid = _setup(db, "stockuser")
    pm.create_project(uid, "Print Job", filament_id=fid, weight_grams=100)
    pid = pm.get_all_projects(uid)[0]['id']

    ok, _ = pm.mark_as_completed(pid)
    assert ok

    filament = db.query_one("SELECT weight_current FROM filaments WHERE id = ?", (fid,))
    assert filament['weight_current'] == 400  # 500 - 100


def test_mark_as_completed_no_negative_stock(db, pm):
    uid, fid = _setup(db, "neguser")
    pm.create_project(uid, "Heavy Print", filament_id=fid, weight_grams=9999)
    pid = pm.get_all_projects(uid)[0]['id']

    pm.mark_as_completed(pid)
    filament = db.query_one("SELECT weight_current FROM filaments WHERE id = ?", (fid,))
    assert filament['weight_current'] == 0  # MAX(0, ...) clamp


def test_mark_as_completed_updates_status_and_timestamp(db, pm):
    uid, _ = _setup(db, "statususer")
    pm.create_project(uid, "Status Test")
    pid = pm.get_all_projects(uid)[0]['id']

    pm.mark_as_completed(pid)
    project = pm.get_project_by_id(pid)
    assert project['status'] == 'Completado'
    assert project['completed_at'] is not None


def test_mark_as_completed_no_filament(db, pm):
    uid, _ = _setup(db, "nofiluser")
    pm.create_project(uid, "No Filament Project", filament_id=None, weight_grams=0)
    pid = pm.get_all_projects(uid)[0]['id']
    ok, _ = pm.mark_as_completed(pid)
    assert ok  # should not crash when filament_id is None


def test_get_project_stats(db, pm):
    uid, _ = _setup(db, "statsuser")
    pm.create_project(uid, "P1")
    pm.create_project(uid, "P2")
    stats = pm.get_project_stats(uid)
    assert stats['total_projects'] == 2
    assert stats['pending'] == 2
