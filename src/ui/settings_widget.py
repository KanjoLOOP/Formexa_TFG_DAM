from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QComboBox, QCheckBox, QTextEdit, QPushButton, QFrame, QMessageBox)
from src.ui.utils import MessageBoxHelper
from PyQt5.QtCore import Qt, pyqtSignal
from src.utils.translator import translator

class SettingsWidget(QWidget):
    logout_requested = pyqtSignal()  # Señal para cerrar sesión
    exit_requested = pyqtSignal()    # Señal para salir de la app
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
        # Conectar cambio de idioma
        translator.language_changed.connect(self.retranslate_ui)
        
        # Cargar idioma guardado y actualizar combo
        saved_lang = translator.get_current_language()
        lang_index = {'es': 0, 'en': 1, 'fr': 2}.get(saved_lang, 0)
        self.lang_combo.setCurrentIndex(lang_index)

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # Título
        self.title = QLabel("Configuración")
        self.title.setStyleSheet("font-size: 24px; font-weight: bold; color: #e0e0e0; margin-bottom: 20px;")
        main_layout.addWidget(self.title)

        # --- Sección General (Idioma y Tema) ---
        general_frame = QFrame()
        general_frame.setObjectName("Card")
        general_layout = QVBoxLayout(general_frame)
        general_layout.setContentsMargins(20, 20, 20, 20)
        
        self.gen_title = QLabel("General")
        self.gen_title.setStyleSheet("font-size: 18px; font-weight: 600; color: #e0e0e0; border: none; margin-bottom: 10px;")
        general_layout.addWidget(self.gen_title)



        # Idioma
        lang_layout = QHBoxLayout()
        self.lang_label = QLabel("Idioma:")
        self.lang_label.setStyleSheet("font-size: 14px; color: #e0e0e0; border: none;")
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["Español", "English", "Français"])
        self.lang_combo.setStyleSheet("""
            QComboBox {
                background-color: #333333;
                color: white;
                border: 1px solid #555;
                padding: 5px;
                border-radius: 4px;
                min-width: 150px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #333333;
                color: white;
                selection-background-color: #555;
                selection-color: white;
            }
        """)
        self.lang_combo.currentIndexChanged.connect(self.on_language_changed)
        lang_layout.addWidget(self.lang_label)
        lang_layout.addWidget(self.lang_combo)
        lang_layout.addStretch()
        general_layout.addLayout(lang_layout)

        main_layout.addWidget(general_frame)

        # --- Sección Sesión ---
        session_frame = QFrame()
        session_frame.setObjectName("Card")
        session_layout = QVBoxLayout(session_frame)
        session_layout.setContentsMargins(20, 20, 20, 20)
        
        self.session_title = QLabel("Sesión")
        self.session_title.setStyleSheet("font-size: 18px; font-weight: 600; color: #e0e0e0; border: none; margin-bottom: 10px;")
        session_layout.addWidget(self.session_title)
        
        self.session_desc = QLabel("Gestiona tu sesión actual:")
        self.session_desc.setStyleSheet("color: #b0b0b0; margin-bottom: 10px; border: none;")
        session_layout.addWidget(self.session_desc)
        
        # Botones de sesión
        session_buttons = QHBoxLayout()
        
        self.btn_logout = QPushButton("Cambiar de Cuenta")
        self.btn_logout.setCursor(Qt.PointingHandCursor)
        self.btn_logout.setStyleSheet("""
            QPushButton {
                background-color: #007BFF;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1a8cff;
            }
            QPushButton:pressed {
                background-color: #0056b3;
            }
        """)
        self.btn_logout.clicked.connect(self.handle_logout)
        
        self.btn_exit = QPushButton("Salir")
        self.btn_exit.setCursor(Qt.PointingHandCursor)
        self.btn_exit.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        self.btn_exit.clicked.connect(self.handle_exit)
        
        session_buttons.addWidget(self.btn_logout)
        session_buttons.addWidget(self.btn_exit)
        session_buttons.addStretch()
        session_layout.addLayout(session_buttons)
        
        main_layout.addWidget(session_frame)

        # --- Sección Reportar Error ---
        report_frame = QFrame()
        report_frame.setObjectName("Card")
        report_layout = QVBoxLayout(report_frame)
        report_layout.setContentsMargins(20, 20, 20, 20)
        
        self.rep_title = QLabel("Reportar Error")
        self.rep_title.setStyleSheet("font-size: 18px; font-weight: 600; color: #e0e0e0; border: none; margin-bottom: 10px;")
        report_layout.addWidget(self.rep_title)
        
        self.report_desc = QLabel("Describe el problema que has encontrado:")
        self.report_desc.setStyleSheet("color: #b0b0b0; margin-bottom: 5px; border: none;")
        report_layout.addWidget(self.report_desc)

        self.error_text = QTextEdit()
        self.error_text.setPlaceholderText("Escribe aquí los detalles del error...")
        self.error_text.setMinimumHeight(100)
        self.error_text.setStyleSheet("""
            QTextEdit {
                background-color: #333;
                color: #e0e0e0;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 10px;
            }
        """)
        report_layout.addWidget(self.error_text)

        btn_layout = QHBoxLayout()
        self.send_btn = QPushButton("Enviar Reporte")
        self.send_btn.setCursor(Qt.PointingHandCursor)
        self.send_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        self.send_btn.clicked.connect(self.submit_report)
        btn_layout.addStretch()
        btn_layout.addWidget(self.send_btn)
        report_layout.addLayout(btn_layout)

        main_layout.addWidget(report_frame)
        
        main_layout.addStretch()
        self.setLayout(main_layout)

    def handle_logout(self):
        """Emite señal para cerrar sesión y volver al login."""
        self.logout_requested.emit()
    
    def handle_exit(self):
        """Emite señal para cerrar la aplicación."""
        self.exit_requested.emit()

    def on_language_changed(self, index):
        """Maneja el cambio de idioma."""
        lang_map = {0: 'es', 1: 'en', 2: 'fr'}
        lang_code = lang_map.get(index, 'es')
        translator.set_language(lang_code)
    
    def retranslate_ui(self):
        """Actualiza todos los textos de la UI con las traducciones."""
        tr = translator.tr
        
        # Título principal
        self.title.setText(tr('settings.title'))
        
        # Sección General
        self.gen_title.setText(tr('settings.general'))
        self.lang_label.setText(tr('settings.language'))
        
        # Sección Sesión
        self.session_title.setText(tr('settings.session'))
        self.session_desc.setText(tr('settings.session_desc'))
        self.btn_logout.setText(tr('settings.change_account'))
        self.btn_exit.setText(tr('settings.exit'))
        
        # Sección Reportar Error
        self.rep_title.setText(tr('settings.report_error'))
        self.report_desc.setText(tr('settings.report_desc'))
        self.error_text.setPlaceholderText(tr('settings.report_placeholder'))
        self.send_btn.setText(tr('settings.send_report'))
    
    def submit_report(self):
        tr = translator.tr
        text = self.error_text.toPlainText()
        if not text.strip():
            MessageBoxHelper.show_warning(self, tr('settings.report_empty'), tr('settings.report_empty_desc'))
            return
        
        # Aquí iría la lógica real de envío
        MessageBoxHelper.show_info(self, tr('settings.report_sent'), tr('settings.report_sent_desc'))
        self.error_text.clear()
