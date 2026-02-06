import sys
import os

# Añadir el directorio raíz al path para que funcionen los imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import QApplication
from src.ui.main_window import MainWindow
from src.logic.auth_manager import AuthManager

class App:
    """Clase principal que maneja el ciclo de vida de la aplicación."""
    
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setStyle("Fusion")  # Forzar estilo Fusion
        self.auth_manager = AuthManager()
        self.login_widget = None
        self.main_window = None
        
    def run(self):
        """Inicia la aplicación."""
        # Inicializar BD si no existe
        self._check_db()
        
        self.main_window = MainWindow(self.auth_manager)
        self.main_window.show()
        return self.app.exec_()

    def _check_db(self):
        """Verifica y crea la base de datos si es necesario."""
        from src.database.db_manager import DBManager
        db = DBManager()
        
        # Si el archivo de BD no existe o está vacío, inicializar
        if not os.path.exists(db.db_file) or os.path.getsize(db.db_file) == 0:
            import sys
            if getattr(sys, 'frozen', False):
                # Ruta en el ejecutable (dependerá de cómo lo empaquetemos en build_exe.py)
                # Asumiendo --add-data "src/database/schema.sql;src/database"
                base_path = sys._MEIPASS
                schema_path = os.path.join(base_path, 'src', 'database', 'schema.sql')
            else:
                # Ruta en desarrollo
                schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database', 'schema.sql')
            
            print(f"Inicializando base de datos desde: {schema_path}")
            if os.path.exists(schema_path):
                db.init_db(schema_path)
            else:
                print(f"Error: No se encontró el esquema en {schema_path}")

def main():
    app = App()
    sys.exit(app.run())

if __name__ == "__main__":
    main()

