import pytest
from src.logic.inventory_manager import InventoryManager


def _user(db, username="invuser"):
    db.execute(
        "INSERT INTO users (username, password_hash, email, is_guest) VALUES (?, 'h', '', 0)",
        (username,)
    )
    return db.query_one("SELECT id FROM users WHERE username = ?", (username,))['id']


def test_add_filament_valid(db):
    mgr = InventoryManager(db_manager=db)
    uid = _user(db)
    ok, msg = mgr.add_filament("Brand", "PLA", "Red", 1000, 20.0, user_id=uid)
    assert ok
    assert "correctamente" in msg


def test_add_filament_negative_weight(db):
    mgr = InventoryManager(db_manager=db)
    ok, _ = mgr.add_filament("Brand", "PLA", "Red", -10, 20.0)
    assert not ok


def test_add_filament_negative_price(db):
    mgr = InventoryManager(db_manager=db)
    ok, _ = mgr.add_filament("Brand", "PLA", "Red", 1000, -5.0)
    assert not ok


def test_get_all_filaments_filtered_by_user(db):
    mgr = InventoryManager(db_manager=db)
    uid1 = _user(db, "u1")
    uid2 = _user(db, "u2")
    mgr.add_filament("A", "PLA", "Black", 1000, 20.0, user_id=uid1)
    mgr.add_filament("B", "PETG", "White", 800, 25.0, user_id=uid1)
    mgr.add_filament("C", "ABS", "Gray", 600, 30.0, user_id=uid2)
    result = mgr.get_all_filaments(uid1)
    assert len(result) == 2
    assert all(f['user_id'] == uid1 for f in result)


def test_delete_filament(db):
    mgr = InventoryManager(db_manager=db)
    uid = _user(db, "deluser")
    mgr.add_filament("X", "PLA", "Blue", 1000, 15.0, user_id=uid)
    fid = mgr.get_all_filaments(uid)[0]['id']
    mgr.delete_filament(fid)
    assert mgr.get_all_filaments(uid) == []


def test_update_filament_weight(db):
    mgr = InventoryManager(db_manager=db)
    uid = _user(db, "wuser")
    mgr.add_filament("W", "PLA", "Red", 1000, 10.0, user_id=uid)
    fid = mgr.get_all_filaments(uid)[0]['id']
    mgr.update_filament_weight(fid, 750)
    updated = mgr.get_filament_by_id(fid)
    assert updated['weight_current'] == 750
