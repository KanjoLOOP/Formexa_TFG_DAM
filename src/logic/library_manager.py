import os
import shutil
import trimesh
from src.database.db_manager import DBManager

class LibraryManager:
    def __init__(self, db_manager=None):
        self.db = db_manager or DBManager()
        # C6: Usar el directorio de datos del usuario (funciona en modo normal y PyInstaller)
        app_data_dir = DBManager._get_user_data_dir()
        self.library_path = os.path.join(app_data_dir, 'models')
        
        if not os.path.exists(self.library_path):
            os.makedirs(self.library_path)

    def add_model(self, file_path, name, description="", user_id=None):
        """Importa un archivo STL a la biblioteca y lo registra en la BD."""
        if not os.path.exists(file_path):
            return False, "El archivo no existe."

        filename = os.path.basename(file_path)
        dest_path = os.path.join(self.library_path, filename)
        
        # Copiar archivo a la carpeta de la biblioteca
        try:
            shutil.copy2(file_path, dest_path)
        except Exception as e:
            return False, f"Error al copiar archivo: {e}"

        # Miniatura (placeholder por ahora)
        thumbnail_path = "" 
        
        # C5b: Guardar en BD incluyendo user_id
        query = """
            INSERT INTO models (name, description, file_path, thumbnail_path, user_id)
            VALUES (?, ?, ?, ?, ?)
        """
        params = (name, description, dest_path, thumbnail_path, user_id)
        
        if self.db.execute_query(query, params):
            return True, "Modelo añadido correctamente."
        else:
            return False, "Error al guardar en base de datos."

    def get_all_models(self, user_id=None):
        """Obtiene los modelos de la BD, filtrando por usuario si se proporciona.
        
        C5b: Si user_id no es None, devuelve solo los modelos de ese usuario.
        """
        if user_id is not None:
            query = "SELECT * FROM models WHERE user_id = ? ORDER BY added_date DESC"
            return self.db.fetch_query(query, (user_id,))
        else:
            query = "SELECT * FROM models ORDER BY added_date DESC"
            return self.db.fetch_query(query)

    def delete_model(self, model_id):
        """Elimina un modelo de la BD y del sistema de archivos."""
        # Primero obtener la ruta
        query_get = "SELECT file_path FROM models WHERE id = ?"
        result = self.db.fetch_query(query_get, (model_id,))
        
        if result:
            file_path = result[0]['file_path']
            # Borrar archivo físico
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except OSError:
                    pass # Continuar aunque falle borrado físico
            
            # Borrar de BD
            query_del = "DELETE FROM models WHERE id = ?"
            self.db.execute_query(query_del, (model_id,))
            return True
        return False
