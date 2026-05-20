from src.database.db_manager import DBManager


class InventoryManager:
    def __init__(self, db_manager=None):
        self.db = db_manager or DBManager()

    def add_filament(self, brand, material_type, color, weight_initial, price,
                     user_id=None, diameter=1.75, density=1.24):
        if weight_initial < 0 or price < 0:
            return False, "El peso y el precio no pueden ser negativos."
        try:
            self.db.execute(
                """INSERT INTO filaments
                   (brand, material_type, color, weight_initial, weight_current,
                    price, diameter, density, user_id)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (brand, material_type, color, weight_initial, weight_initial,
                 price, diameter, density, user_id)
            )
            return True, "Filamento añadido correctamente."
        except Exception:
            return False, "Error al añadir filamento."

    def get_all_filaments(self, user_id=None):
        if user_id is not None:
            return self.db.query(
                "SELECT * FROM filaments WHERE user_id = ? ORDER BY id DESC",
                (user_id,)
            )
        return self.db.query("SELECT * FROM filaments ORDER BY id DESC")

    def update_filament_weight(self, filament_id, new_weight):
        self.db.execute(
            "UPDATE filaments SET weight_current = ? WHERE id = ?",
            (new_weight, filament_id)
        )
        return True

    def delete_filament(self, filament_id):
        self.db.execute("DELETE FROM filaments WHERE id = ?", (filament_id,))
        return True

    def get_filament_by_id(self, filament_id):
        return self.db.query_one(
            "SELECT * FROM filaments WHERE id = ?", (filament_id,)
        )
