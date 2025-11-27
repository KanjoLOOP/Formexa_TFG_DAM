import sqlite3
from datetime import datetime
from src.database.db_manager import DBManager

class ProjectManager:
    """Gestor de proyectos de impresión 3D."""
    
    def __init__(self):
        self.db = DBManager()
    
    def create_project(self, user_id, name, description="", model_id=None, filament_id=None, 
                      weight_grams=0, print_time_hours=0, status="Pendiente"):
        """Crea un nuevo proyecto."""
        try:
            query = """
                INSERT INTO projects (user_id, name, description, model_id, filament_id,
                                    weight_grams, print_time_hours, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            self.db.execute_query(query, (user_id, name, description, model_id, filament_id,
                                         weight_grams, print_time_hours, status))
            return True, "Proyecto creado exitosamente"
        except Exception as e:
            return False, f"Error al crear proyecto: {str(e)}"
    
    def get_all_projects(self, user_id):
        """Obtiene todos los proyectos de un usuario."""
        query = """
            SELECT p.id, p.name, p.description, p.status, p.weight_grams, p.print_time_hours,
                   p.total_cost, p.filament_cost, p.energy_cost, p.created_at, p.completed_at,
                   m.name as model_name, f.brand as filament_brand, f.material_type
            FROM projects p
            LEFT JOIN models m ON p.model_id = m.id
            LEFT JOIN filaments f ON p.filament_id = f.id
            WHERE p.user_id = ?
            ORDER BY p.created_at DESC
        """
        return self.db.fetch_all(query, (user_id,))
    
    def get_project_by_id(self, project_id):
        """Obtiene un proyecto por ID."""
        query = """
            SELECT p.*, m.name as model_name, f.brand as filament_brand, f.material_type
            FROM projects p
            LEFT JOIN models m ON p.model_id = m.id
            LEFT JOIN filaments f ON p.filament_id = f.id
            WHERE p.id = ?
        """
        return self.db.fetch_one(query, (project_id,))
    
    def update_project(self, project_id, **kwargs):
        """Actualiza un proyecto."""
        try:
            # Construir query dinámicamente según los campos proporcionados
            fields = []
            values = []
            
            allowed_fields = ['name', 'description', 'status', 'weight_grams', 'print_time_hours',
                            'total_cost', 'filament_cost', 'energy_cost', 'model_id', 'filament_id']
            
            for field, value in kwargs.items():
                if field in allowed_fields:
                    fields.append(f"{field} = ?")
                    values.append(value)
            
            if not fields:
                return False, "No hay campos para actualizar"
            
            values.append(project_id)
            query = f"UPDATE projects SET {', '.join(fields)} WHERE id = ?"
            
            self.db.execute_query(query, tuple(values))
            return True, "Proyecto actualizado exitosamente"
        except Exception as e:
            return False, f"Error al actualizar proyecto: {str(e)}"
    
    def delete_project(self, project_id):
        """Elimina un proyecto."""
        try:
            query = "DELETE FROM projects WHERE id = ?"
            self.db.execute_query(query, (project_id,))
            return True, "Proyecto eliminado exitosamente"
        except Exception as e:
            return False, f"Error al eliminar proyecto: {str(e)}"
    
    def calculate_costs(self, weight_grams, filament_price_per_kg, print_time_hours, 
                       power_watts=350, energy_cost_per_kwh=0.15):
        """Calcula los costes de un proyecto."""
        # Coste de filamento
        filament_cost = (weight_grams / 1000) * filament_price_per_kg
        
        # Coste energético
        energy_kwh = (power_watts * print_time_hours) / 1000
        energy_cost = energy_kwh * energy_cost_per_kwh
        
        # Coste total
        total_cost = filament_cost + energy_cost
        
        return {
            'filament_cost': round(filament_cost, 2),
            'energy_cost': round(energy_cost, 2),
            'total_cost': round(total_cost, 2)
        }
    
    def mark_as_completed(self, project_id):
        """Marca un proyecto como completado."""
        try:
            query = "UPDATE projects SET status = 'Completado', completed_at = ? WHERE id = ?"
            self.db.execute_query(query, (datetime.now(), project_id))
            return True, "Proyecto marcado como completado"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def get_project_stats(self, user_id):
        """Obtiene estadísticas de proyectos de un usuario."""
        query = """
            SELECT 
                COUNT(*) as total_projects,
                SUM(CASE WHEN status = 'Completado' THEN 1 ELSE 0 END) as completed,
                SUM(CASE WHEN status = 'Pendiente' THEN 1 ELSE 0 END) as pending,
                SUM(CASE WHEN status = 'En Progreso' THEN 1 ELSE 0 END) as in_progress,
                SUM(total_cost) as total_spent,
                SUM(print_time_hours) as total_hours
            FROM projects
            WHERE user_id = ?
        """
        return self.db.fetch_one(query, (user_id,))
