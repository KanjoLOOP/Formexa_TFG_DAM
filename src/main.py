import sys
import os

__version__ = "1.0.0"

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import QApplication, QMessageBox
from src.ui.main_window import MainWindow
from src.logic.auth_manager import AuthManager
from src.database.db_manager import DBManager
from src.database.migrations import run_migrations
from src.utils.logger import logger
from src.utils.resource_path import get_asset_path


def bootstrap_db() -> bool:
    db = DBManager()
    if not db.connect():
        logger.critical("No se pudo conectar a la BD")
        return False
    schema_path = get_asset_path(os.path.join('src', 'database', 'schema.sql'))
    if not os.path.exists(schema_path):
        logger.critical(f"schema.sql no encontrado: {schema_path}")
        return False
    db.init_db(schema_path)  # idempotente — CREATE IF NOT EXISTS
    try:
        run_migrations(db)
    except Exception as e:
        logger.error(f"Error en migraciones: {e}")
    return True


def _show_db_warning():
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Warning)
    msg.setWindowTitle("Base de datos no disponible")
    msg.setText(
        "No se pudo inicializar la base de datos.\n\n"
        "Puedes continuar en Modo Invitado (solo calculadora)."
    )
    msg.setStandardButtons(QMessageBox.Ok)
    msg.exec_()


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    db_ok = bootstrap_db()
    if not db_ok:
        _show_db_warning()

    auth = AuthManager()
    win = MainWindow(auth)
    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
