from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QLineEdit, QFrame, QMessageBox, QCheckBox)
from src.ui.utils import MessageBoxHelper
from src.logic.session_manager import SessionManager
from src.utils.resource_path import get_asset_path
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap
import os

class LoginWidget(QWidget):
    """Widget de login con soporte para registro y modo invitado."""
    
    login_successful = pyqtSignal(dict)  # Emite el usuario cuando login es exitoso
    
    def __init__(self, auth_manager):
        super().__init__()
        self.auth_manager = auth_manager
        self.is_register_mode = False
        self.init_ui()
        self.load_saved_session()
    
    def init_ui(self):
        self.setObjectName("LoginWidget")
        self.setWindowTitle("Iniciar Sesión")
        self.setStyleSheet("#LoginWidget { background-color: #1E1E1E; }")
        
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        
        # Contenedor central
        container = QFrame()
        container.setObjectName("Card")
        container.setFixedWidth(400)
        container_layout = QVBoxLayout(container)
        container_layout.setSpacing(20)
        container_layout.setContentsMargins(40, 40, 40, 40)
        
        # Logo
        logo_label = QLabel()
        logo_path = get_asset_path(os.path.join('assets', 'logo.png'))
        
        logo_pixmap = QPixmap(logo_path)
        if not logo_pixmap.isNull():
            scaled_pixmap = logo_pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(scaled_pixmap)
            logo_label.setAlignment(Qt.AlignCenter)
            # Añadir margen superior para bajarlo un poco
            logo_label.setStyleSheet("padding-top: 20px; margin-bottom: 20px;")
        else:
            logo_label.setText("Formexa") # Fallback
            logo_label.setStyleSheet("font-size: 32px; font-weight: bold; color: white; padding-top: 20px; margin-bottom: 20px;")
            logo_label.setAlignment(Qt.AlignCenter)
            
        container_layout.addWidget(logo_label)
        
        # Campos de entrada
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Usuario")
        self.username_input.setObjectName("input_login")
        container_layout.addWidget(self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Contraseña")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setObjectName("input_login")
        self.password_input.returnPressed.connect(self.handle_login_or_register)
        container_layout.addWidget(self.password_input)

        # Campo email (solo para registro)
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email (opcional)")
        self.email_input.setObjectName("input_login")
        self.email_input.setVisible(False)
        container_layout.addWidget(self.email_input)

        # Checkbox Recuérdame
        self.remember_me = QCheckBox("Recuérdame")
        self.remember_me.setObjectName("remember_me")
        container_layout.addWidget(self.remember_me)

        # Botón principal (Login/Registrar)
        self.btn_main = QPushButton("Iniciar Sesión")
        self.btn_main.setCursor(Qt.PointingHandCursor)
        self.btn_main.setObjectName("btn_primary")
        self.btn_main.clicked.connect(self.handle_login_or_register)
        container_layout.addWidget(self.btn_main)

        # Botón toggle (Registrarse/Volver a Login)
        self.btn_toggle = QPushButton("¿No tienes cuenta? Regístrate")
        self.btn_toggle.setCursor(Qt.PointingHandCursor)
        self.btn_toggle.setObjectName("btn_link")
        self.btn_toggle.clicked.connect(self.toggle_mode)
        container_layout.addWidget(self.btn_toggle)

        # Separador
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("background-color: #444; margin: 10px 0;")
        container_layout.addWidget(separator)

        # Botón invitado
        btn_guest = QPushButton("Continuar como Invitado")
        btn_guest.setCursor(Qt.PointingHandCursor)
        btn_guest.setObjectName("btn_guest")
        btn_guest.clicked.connect(self.handle_guest_login)
        container_layout.addWidget(btn_guest)
        
        # Nota sobre modo invitado
        guest_note = QLabel("Modo invitado: Solo calculadora disponible")
        guest_note.setStyleSheet("color: #888; font-size: 12px; margin-top: 5px;")
        guest_note.setAlignment(Qt.AlignCenter)
        container_layout.addWidget(guest_note)
        
        layout.addWidget(container)
        self.setLayout(layout)
    
    def load_saved_session(self):
        """Auto-login if a valid session token exists in APPDATA."""
        user_id = SessionManager.load_session()
        if user_id is not None:
            if self.auth_manager.login_from_session(user_id):
                user = self.auth_manager.get_current_user()
                self.login_successful.emit(user)

    def toggle_mode(self):
        """Alterna entre modo login y registro."""
        self.is_register_mode = not self.is_register_mode
        
        if self.is_register_mode:
            self.btn_main.setText("Registrarse")
            self.btn_toggle.setText("¿Ya tienes cuenta? Inicia sesión")
            self.email_input.setVisible(True)
            self.remember_me.setVisible(False) # Ocultar en registro
        else:
            self.btn_main.setText("Iniciar Sesión")
            self.btn_toggle.setText("¿No tienes cuenta? Regístrate")
            self.email_input.setVisible(False)
            self.remember_me.setVisible(True) # Mostrar en login
    
    def handle_login_or_register(self):
        """Maneja login o registro según el modo actual."""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        if not username or not password:
            self.show_message("Error", "Usuario y contraseña son obligatorios", QMessageBox.Warning)
            return
        
        if self.is_register_mode:
            email = self.email_input.text().strip()
            success, message = self.auth_manager.register(username, password, email)
            
            if success:
                self.show_message("Éxito", message, QMessageBox.Information)
                self.toggle_mode()  # Volver a modo login
                self.password_input.clear()
            else:
                self.show_message("Error", message, QMessageBox.Warning)
        else:
            success, message = self.auth_manager.login(username, password)
            
            if success:
                user = self.auth_manager.get_current_user()
                if self.remember_me.isChecked():
                    SessionManager.save_session(user['id'])
                else:
                    SessionManager.clear_session()
                self.login_successful.emit(user)
            else:
                self.show_message("Error", message, QMessageBox.Warning)
    
    def handle_guest_login(self):
        """Maneja el login como invitado."""
        self.auth_manager.login_as_guest()
        user = self.auth_manager.get_current_user()
        self.login_successful.emit(user)
    
    def show_message(self, title, text, icon):
        """Muestra un mensaje al usuario."""
        if icon == QMessageBox.Information:
            MessageBoxHelper.show_info(self.window(), title, text)
        elif icon == QMessageBox.Warning:
            MessageBoxHelper.show_warning(self.window(), title, text)
        elif icon == QMessageBox.Critical:
            MessageBoxHelper.show_error(self.window(), title, text)
        else:
            MessageBoxHelper.show_info(self.window(), title, text)
