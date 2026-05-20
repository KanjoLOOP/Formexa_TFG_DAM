from datetime import datetime
from src.database.db_manager import DBManager


class ProjectManager:

    def __init__(self):
        self.db = DBManager()

    def create_project(self, user_id, name, description="", model_id=None,
                       filament_id=None, weight_grams=0, print_time_hours=0,
                       status="Pendiente"):
        try:
            self.db.execute(
                """INSERT INTO projects
                   (user_id, name, description, model_id, filament_id,
                    weight_grams, print_time_hours, status)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (user_id, name, description, model_id, filament_id,
                 weight_grams, print_time_hours, status)
            )
            return True, "Proyecto creado exitosamente"
        except Exception as e:
            return False, f"Error al crear proyecto: {str(e)}"

    def get_all_projects(self, user_id):
        """Returns list[dict] ordered by created_at DESC."""
        return self.db.query(
            """SELECT p.id, p.name, p.description, p.status, p.weight_grams,
                      p.print_time_hours, p.total_cost, p.filament_cost,
                      p.energy_cost, p.created_at, p.completed_at,
                      m.name as model_name, f.brand as filament_brand,
                      f.material_type
               FROM projects p
               LEFT JOIN models m ON p.model_id = m.id
               LEFT JOIN filaments f ON p.filament_id = f.id
               WHERE p.user_id = ?
               ORDER BY p.created_at DESC""",
            (user_id,)
        )

    def get_project_by_id(self, project_id):
        return self.db.query_one(
            """SELECT p.*, m.name as model_name,
                      f.brand as filament_brand, f.material_type
               FROM projects p
               LEFT JOIN models m ON p.model_id = m.id
               LEFT JOIN filaments f ON p.filament_id = f.id
               WHERE p.id = ?""",
            (project_id,)
        )

    def update_project(self, project_id, **kwargs):
        allowed = {
            'name', 'description', 'status', 'weight_grams', 'print_time_hours',
            'total_cost', 'filament_cost', 'energy_cost', 'model_id',
            'filament_id', 'completed_at',
        }
        fields = [f"{k} = ?" for k in kwargs if k in allowed]
        values = [v for k, v in kwargs.items() if k in allowed]
        if not fields:
            return False, "No hay campos para actualizar"
        try:
            self.db.execute(
                f"UPDATE projects SET {', '.join(fields)} WHERE id = ?",
                (*values, project_id)
            )
            return True, "Proyecto actualizado exitosamente"
        except Exception as e:
            return False, f"Error al actualizar proyecto: {str(e)}"

    def delete_project(self, project_id):
        try:
            self.db.execute("DELETE FROM projects WHERE id = ?", (project_id,))
            return True, "Proyecto eliminado exitosamente"
        except Exception as e:
            return False, f"Error al eliminar proyecto: {str(e)}"

    def calculate_costs(self, weight_grams, filament_price_per_kg,
                        print_time_hours, power_watts=350,
                        energy_cost_per_kwh=0.15):
        filament_cost = (weight_grams / 1000) * filament_price_per_kg
        energy_cost = ((power_watts * print_time_hours) / 1000) * energy_cost_per_kwh
        return {
            'filament_cost': round(filament_cost, 2),
            'energy_cost': round(energy_cost, 2),
            'total_cost': round(filament_cost + energy_cost, 2),
        }

    def mark_as_completed(self, project_id):
        try:
            with self.db.transaction():
                project = self.get_project_by_id(project_id)
                if not project:
                    raise ValueError("Proyecto no encontrado")
                if project['filament_id'] and project['weight_grams']:
                    self.db.execute(
                        "UPDATE filaments SET weight_current = MAX(0, weight_current - ?) WHERE id = ?",
                        (project['weight_grams'], project['filament_id'])
                    )
                self.db.execute(
                    "UPDATE projects SET status = 'Completado', completed_at = ? WHERE id = ?",
                    (datetime.now().isoformat(), project_id)
                )
            return True, "Proyecto marcado como completado"
        except Exception as e:
            return False, f"Error: {str(e)}"

    def get_project_stats(self, user_id):
        return self.db.query_one(
            """SELECT
                   COUNT(*) as total_projects,
                   SUM(CASE WHEN status = 'Completado' THEN 1 ELSE 0 END) as completed,
                   SUM(CASE WHEN status = 'Pendiente' THEN 1 ELSE 0 END) as pending,
                   SUM(CASE WHEN status = 'En Progreso' THEN 1 ELSE 0 END) as in_progress,
                   SUM(total_cost) as total_spent,
                   SUM(print_time_hours) as total_hours
               FROM projects WHERE user_id = ?""",
            (user_id,)
        )
