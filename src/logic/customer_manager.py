import sqlite3
from src.database.db_manager import DBManager


class CustomerManager:

    def __init__(self):
        self.db = DBManager()

    def create_customer(self, user_id, name, email="", phone="", address="", notes="") -> tuple:
        if not name.strip():
            return False, "El nombre es obligatorio"
        try:
            self.db.execute(
                """INSERT INTO customers (user_id, name, email, phone, address, notes)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (user_id, name.strip(), email, phone, address, notes)
            )
            return True, "Cliente creado correctamente"
        except sqlite3.Error as e:
            return False, f"Error al crear cliente: {e}"

    def get_all_customers(self, user_id) -> list:
        return self.db.query(
            "SELECT * FROM customers WHERE user_id = ? ORDER BY name ASC",
            (user_id,)
        )

    def get_customer_by_id(self, customer_id):
        return self.db.query_one(
            "SELECT * FROM customers WHERE id = ?", (customer_id,)
        )

    def update_customer(self, customer_id, **kwargs) -> tuple:
        allowed = {'name', 'email', 'phone', 'address', 'notes'}
        fields = [f"{k} = ?" for k in kwargs if k in allowed]
        values = [v for k, v in kwargs.items() if k in allowed]
        if not fields:
            return False, "Sin campos para actualizar"
        try:
            self.db.execute(
                f"UPDATE customers SET {', '.join(fields)} WHERE id = ?",
                (*values, customer_id)
            )
            return True, "Cliente actualizado correctamente"
        except sqlite3.Error as e:
            return False, f"Error al actualizar: {e}"

    def delete_customer(self, customer_id) -> tuple:
        try:
            self.db.execute("DELETE FROM customers WHERE id = ?", (customer_id,))
            return True, "Cliente eliminado"
        except sqlite3.IntegrityError:
            return False, "No se puede eliminar: tiene pedidos asociados"
        except sqlite3.Error as e:
            return False, f"Error al eliminar: {e}"
