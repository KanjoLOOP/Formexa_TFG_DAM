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
        """Verifica la integridad de la BD y la inicializa explícitamente si faltan tablas."""
        from src.database.db_manager import DBManager
        import sqlite3
        
        self.log_debug("--- Inicio de verificación de BD ---")
        
        db = DBManager()
        self.log_debug(f"Ruta de BD esperada: {db.db_file}")
        
        needs_init = False
        
        # 1. Verificar si la tabla 'users' existe realmente
        try:
            if not db.connect():
                self.log_debug("Fallo al conectar a BD")
                needs_init = True
            else:
                cursor = db.connection.cursor()
                cursor.execute("SELECT count(*) FROM users")
                rows = cursor.fetchone()
                self.log_debug(f"Tabla users encontrada. Filas: {rows[0]}")
                cursor.close()
        except sqlite3.OperationalError as e:
            self.log_debug(f"Error Operacional (tabla no existe?): {e}")
            needs_init = True
        except Exception as e:
            self.log_debug(f"Error Genérico verificando BD: {e}")
            needs_init = True
            
        # 2. Inicializar si es necesario
        if needs_init:
            self.log_debug("Se requiere inicialización de BD.")
            import sys
            if getattr(sys, 'frozen', False):
                # Ruta en el ejecutable
                base_path = sys._MEIPASS
                self.log_debug(f"Modo Frozen detectado. Base path (_MEIPASS): {base_path}")
                
                # Listar contenido de _MEIPASS para debugging
                try:
                    meipass_contents = os.listdir(base_path)
                    self.log_debug(f"Contenido de _MEIPASS (primeros 20): {meipass_contents[:20]}")
                    
                    src_path = os.path.join(base_path, 'src')
                    if os.path.exists(src_path):
                        src_contents = os.listdir(src_path)
                        self.log_debug(f"Contenido de src/: {src_contents}")
                        
                        src_db_path = os.path.join(src_path, 'database')
                        if os.path.exists(src_db_path):
                            db_contents = os.listdir(src_db_path)
                            self.log_debug(f"Contenido de src/database/: {db_contents}")
                    else:
                        self.log_debug("ERROR: No existe directorio 'src' en _MEIPASS")
                except Exception as e:
                    self.log_debug(f"Error listando contenidos: {e}")
                
                schema_path = os.path.join(base_path, 'src', 'database', 'schema.sql')
            else:
                # Ruta en desarrollo
                schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database', 'schema.sql')
                self.log_debug("Modo Desarrollo detectado.")
            
            self.log_debug(f"Buscando schema en: {schema_path}")
            
            if not os.path.exists(schema_path):
                self.log_debug("ADVERTENCIA: El archivo schema.sql NO existe en la ruta.")
                self._show_warning(
                    "Base de Datos No Disponible", 
                    f"No se pudo inicializar la base de datos.\n\n"
                    f"Puedes continuar usando el Modo Invitado (solo calculadora).\n\n"
                    f"Ruta buscada: {schema_path}"
                )
                return
            
            # Leer primeros bytes para verificar contenido
            try:
                with open(schema_path, 'r', encoding='utf-8') as f:
                    content_preview = f.read(100)
                    self.log_debug(f"Contenido schema.sql (inicio): {content_preview[:50]}...")
            except Exception as e:
                self.log_debug(f"Error leyendo archivo schema: {e}")

            if not db.init_db(schema_path):
                self.log_debug("ADVERTENCIA: db.init_db devolvió False")
                self._show_warning(
                    "Error de Inicialización", 
                    f"No se pudo crear la base de datos.\n\n"
                    f"Puedes continuar usando el Modo Invitado (solo calculadora).\n\n"
                    f"Revisa debug_log.txt para más detalles."
                )
            else:
                self.log_debug("db.init_db devolvió True. Inicialización exitosa.")

    def log_debug(self, msg):
        """Escribe mensaje en debug_log.txt junto al ejecutable."""
        try:
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Determinar ruta del log
            if getattr(sys, 'frozen', False):
                base_dir = os.path.dirname(sys.executable)
            else:
                base_dir = os.path.dirname(os.path.abspath(__file__))
                
            log_path = os.path.join(base_dir, 'debug_log.txt')
            
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(f"[{timestamp}] {msg}\n")
        except Exception:
            pass # No podemos hacer mucho si falla el log

    def _show_warning(self, title, message):
        """Muestra un mensaje de advertencia NO bloqueante."""
        from PyQt5.QtWidgets import QMessageBox
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

def main():
    app = App()
    sys.exit(app.run())

if __name__ == "__main__":
    main()

