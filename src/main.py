import sys
import os

# Añadir el directorio raíz al path para que funcionen los imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import QApplication
from src.ui.main_window import MainWindow
from src.ui.login_widget import LoginWidget
from src.logic.auth_manager import AuthManager

def main():
    app = QApplication(sys.argv)
    
    # Crear gestor de autenticación
    auth_manager = AuthManager()
    
    # Mostrar pantalla de login
    login_widget = LoginWidget(auth_manager)
    
    def on_login_successful(user):
        """Callback cuando el login es exitoso."""
        login_widget.close()
        window = MainWindow(auth_manager)
        window.show()
    
    login_widget.login_successful.connect(on_login_successful)
    login_widget.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

