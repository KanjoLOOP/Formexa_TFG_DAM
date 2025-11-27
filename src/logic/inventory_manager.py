from src.database.db_manager import DBManager

class InventoryManager:
    def __init__(self, db_manager=None):
        self.db = db_manager or DBManager()

    def add_filament(self, brand, material_type, color, weight_initial, price, diameter=1.75, density=1.24):
        """Añade un nuevo rollo de filamento."""
        query = """
            INSERT INTO filaments (brand, material_type, color, weight_initial, weight_current, price, diameter, density)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        # Al inicio, peso actual = peso inicial
        params = (brand, material_type, color, weight_initial, weight_initial, price, diameter, density)
        
        if self.db.execute_query(query, params):
            return True, "Filamento añadido correctamente."
        else:
            return False, "Error al añadir filamento."

    def get_all_filaments(self):
        """Obtiene todos los filamentos."""
        query = "SELECT * FROM filaments ORDER BY id DESC"
        return self.db.fetch_query(query)

    def update_filament_weight(self, filament_id, new_weight):
        """Actualiza el peso restante de un filamento."""
        query = "UPDATE filaments SET weight_current = ? WHERE id = ?"
        if self.db.execute_query(query, (new_weight, filament_id)):
            return True
        return False

    def delete_filament(self, filament_id):
        """Elimina un filamento."""
        query = "DELETE FROM filaments WHERE id = ?"
        if self.db.execute_query(query, (filament_id,)):
            return True
        return False
    
    def get_filament_by_id(self, filament_id):
        """Obtiene un filamento por ID."""
        query = "SELECT * FROM filaments WHERE id = ?"
        return self.db.fetch_one(query, (filament_id,))

