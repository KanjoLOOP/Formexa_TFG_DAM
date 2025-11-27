from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QLineEdit, QFrame, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

class LoginWidget(QWidget):
    """Widget de login con soporte para registro y modo invitado."""
    
    login_successful = pyqtSignal(dict)  # Emite el usuario cuando login es exitoso
    
    def __init__(self, auth_manager):
        super().__init__()
        self.auth_manager = auth_manager
        self.is_register_mode = False
        self.init_ui()
    
    def init_ui(self):
        self.setStyleSheet("background-color: #1E1E1E;")
        
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        
        # Contenedor central
        container = QFrame()
        container.setObjectName("Card")
        container.setFixedWidth(400)
        container_layout = QVBoxLayout(container)
        container_layout.setSpacing(20)
        container_layout.setContentsMargins(40, 40, 40, 40)
        
        # Título
        title = QLabel("Gestor 3D")
        title.setStyleSheet("font-size: 32px; font-weight: bold; color: white;")
        title.setAlignment(Qt.AlignCenter)
        container_layout.addWidget(title)
        
        subtitle = QLabel("Gestión de Impresión 3D")
        subtitle.setStyleSheet("font-size: 14px; color: #999; margin-bottom: 20px;")
        subtitle.setAlignment(Qt.AlignCenter)
        container_layout.addWidget(subtitle)
        
        # Campos de entrada
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Usuario")
        self.username_input.setStyleSheet("""
            QLineEdit {
                background-color: #2C2C2C;
                border: 1px solid #444;
                border-radius: 6px;
                padding: 12px;
                color: white;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #007BFF;
            }
        """)
        container_layout.addWidget(self.username_input)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Contraseña")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet(self.username_input.styleSheet())
        self.password_input.returnPressed.connect(self.handle_login_or_register)
        container_layout.addWidget(self.password_input)
        
        # Campo email (solo para registro)
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email (opcional)")
        self.email_input.setStyleSheet(self.username_input.styleSheet())
        self.email_input.setVisible(False)
        container_layout.addWidget(self.email_input)
        
        # Botón principal (Login/Registrar)
        self.btn_main = QPushButton("Iniciar Sesión")
        self.btn_main.setCursor(Qt.PointingHandCursor)
        self.btn_main.setStyleSheet("""
            QPushButton {
                background-color: #007BFF;
                color: white;
                border-radius: 6px;
                padding: 12px;
                font-weight: bold;
                font-size: 14px;
                border: none;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:pressed {
                background-color: #004085;
            }
        """)
        self.btn_main.clicked.connect(self.handle_login_or_register)
        container_layout.addWidget(self.btn_main)
        
        # Botón toggle (Registrarse/Volver a Login)
        self.btn_toggle = QPushButton("¿No tienes cuenta? Regístrate")
        self.btn_toggle.setCursor(Qt.PointingHandCursor)
        self.btn_toggle.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #007BFF;
                border: none;
                padding: 8px;
                font-size: 13px;
            }
            QPushButton:hover {
                text-decoration: underline;
            }
        """)
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
        btn_guest.setStyleSheet("""
            QPushButton {
                background-color: #444;
                color: #ccc;
                border-radius: 6px;
                padding: 12px;
                font-size: 14px;
                border: none;
            }
            QPushButton:hover {
                background-color: #555;
            }
        """)
        btn_guest.clicked.connect(self.handle_guest_login)
        container_layout.addWidget(btn_guest)
        
        # Nota sobre modo invitado
        guest_note = QLabel("Modo invitado: Solo calculadora disponible")
        guest_note.setStyleSheet("color: #888; font-size: 12px; margin-top: 5px;")
        guest_note.setAlignment(Qt.AlignCenter)
        container_layout.addWidget(guest_note)
        
        layout.addWidget(container)
        self.setLayout(layout)
    
    def toggle_mode(self):
        """Alterna entre modo login y registro."""
        self.is_register_mode = not self.is_register_mode
        
        if self.is_register_mode:
            self.btn_main.setText("Registrarse")
            self.btn_toggle.setText("¿Ya tienes cuenta? Inicia sesión")
            self.email_input.setVisible(True)
        else:
            self.btn_main.setText("Iniciar Sesión")
            self.btn_toggle.setText("¿No tienes cuenta? Regístrate")
            self.email_input.setVisible(False)
    
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
        msg_box = QMessageBox(self.window())
        msg_box.setWindowTitle(title)
        msg_box.setText(text)
        msg_box.setIcon(icon)
        msg_box.addButton("Aceptar", QMessageBox.AcceptRole)
        msg_box.exec_()
