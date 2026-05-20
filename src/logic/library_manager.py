import os
import shutil

from src.database.db_manager import DBManager


class LibraryManager:
    def __init__(self, db_manager=None):
        self.db = db_manager or DBManager()
        app_data_dir = DBManager._get_user_data_dir()
        self.library_path = os.path.join(app_data_dir, 'models')
        if not os.path.exists(self.library_path):
            os.makedirs(self.library_path)

    def add_model(self, file_path, name, description="", user_id=None):
        if not os.path.exists(file_path):
            return False, "El archivo no existe."
        dest_path = os.path.join(self.library_path, os.path.basename(file_path))
        try:
            shutil.copy2(file_path, dest_path)
        except Exception as e:
            return False, f"Error al copiar archivo: {e}"
        try:
            self.db.execute(
                "INSERT INTO models (name, description, file_path, thumbnail_path, user_id) VALUES (?, ?, ?, ?, ?)",
                (name, description, dest_path, "", user_id)
            )
            return True, "Modelo añadido correctamente."
        except Exception as e:
            return False, f"Error al guardar en base de datos: {e}"

    def get_all_models(self, user_id=None):
        if user_id is not None:
            return self.db.query(
                "SELECT * FROM models WHERE user_id = ? ORDER BY added_date DESC",
                (user_id,)
            )
        return self.db.query("SELECT * FROM models ORDER BY added_date DESC")

    def delete_model(self, model_id):
        result = self.db.query_one(
            "SELECT file_path FROM models WHERE id = ?", (model_id,)
        )
        if result:
            file_path = result['file_path']
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except OSError:
                    pass
            self.db.execute("DELETE FROM models WHERE id = ?", (model_id,))
            return True
        return False
