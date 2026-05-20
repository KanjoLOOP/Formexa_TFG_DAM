import sqlite3
from datetime import datetime
from src.database.db_manager import DBManager


class OrderManager:

    STATUSES = ['Presupuesto', 'Aceptado', 'En Producción', 'Entregado', 'Cancelado']

    def __init__(self):
        self.db = DBManager()

    def create_order(self, user_id, customer_id, unit_price, quantity=1,
                     project_id=None, delivery_date=None) -> tuple:
        try:
            total_price = round(unit_price * quantity, 2)
            self.db.execute(
                """INSERT INTO orders
                   (user_id, customer_id, project_id, unit_price, total_price,
                    quantity, delivery_date)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (user_id, customer_id, project_id, unit_price, total_price,
                 quantity, delivery_date)
            )
            return True, "Pedido creado correctamente"
        except sqlite3.Error as e:
            return False, f"Error al crear pedido: {e}"

    def get_all_orders(self, user_id) -> list:
        return self.db.query(
            """SELECT o.*, c.name as customer_name, p.name as project_name
               FROM orders o
               JOIN customers c ON o.customer_id = c.id
               LEFT JOIN projects p ON o.project_id = p.id
               WHERE o.user_id = ?
               ORDER BY o.created_at DESC""",
            (user_id,)
        )

    def get_order_by_id(self, order_id):
        return self.db.query_one(
            """SELECT o.*, c.name as customer_name, p.name as project_name
               FROM orders o
               JOIN customers c ON o.customer_id = c.id
               LEFT JOIN projects p ON o.project_id = p.id
               WHERE o.id = ?""",
            (order_id,)
        )

    def update_order(self, order_id, **kwargs) -> tuple:
        allowed = {'status', 'quantity', 'unit_price', 'total_price',
                   'delivery_date', 'project_id', 'customer_id'}
        fields = [f"{k} = ?" for k in kwargs if k in allowed]
        values = [v for k, v in kwargs.items() if k in allowed]
        if not fields:
            return False, "Sin campos para actualizar"
        try:
            self.db.execute(
                f"UPDATE orders SET {', '.join(fields)} WHERE id = ?",
                (*values, order_id)
            )
            return True, "Pedido actualizado"
        except sqlite3.Error as e:
            return False, f"Error al actualizar: {e}"

    def mark_as_delivered(self, order_id) -> tuple:
        try:
            self.db.execute(
                "UPDATE orders SET status = 'Entregado', delivered_at = ? WHERE id = ?",
                (datetime.now().isoformat(), order_id)
            )
            return True, "Pedido marcado como entregado"
        except sqlite3.Error as e:
            return False, f"Error: {e}"

    def delete_order(self, order_id) -> tuple:
        try:
            self.db.execute("DELETE FROM orders WHERE id = ?", (order_id,))
            return True, "Pedido eliminado"
        except sqlite3.Error as e:
            return False, f"Error al eliminar: {e}"

    def get_revenue_stats(self, user_id) -> dict:
        return self.db.query_one(
            """SELECT
                   COUNT(*) as total_orders,
                   SUM(CASE WHEN status = 'Entregado' THEN total_price ELSE 0 END) as revenue,
                   SUM(CASE WHEN status NOT IN ('Entregado','Cancelado') THEN total_price ELSE 0 END) as pending_revenue,
                   COUNT(CASE WHEN status = 'Entregado' THEN 1 END) as delivered,
                   COUNT(CASE WHEN status = 'Cancelado' THEN 1 END) as cancelled
               FROM orders WHERE user_id = ?""",
            (user_id,)
        )
