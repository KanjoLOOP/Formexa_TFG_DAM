from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QStackedWidget, QFrame, QLabel, QMessageBox)
from src.ui.utils import MessageBoxHelper
from src.utils.resource_path import get_asset_path
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QPixmap

from src.ui.home_widget import HomeWidget
from src.ui.calculator_widget import CalculatorWidget
from src.ui.library_widget import LibraryWidget
from src.ui.inventory_widget import InventoryWidget
from src.ui.marketplace_widget import MarketplaceWidget
from src.ui.settings_widget import SettingsWidget
from src.ui.projects_widget import ProjectsWidget

class MainWindow(QMainWindow):
    logout_requested = pyqtSignal()  # Señal para volver al login
    
    def __init__(self, auth_manager):
        super().__init__()
        self.auth_manager = auth_manager
        self.user = None
        
        self.setWindowTitle("Formexa")
        self.resize(1100, 750)
        
        # Cargar estilos
        self.load_styles()

        # Stack Principal (Login vs App)
        self.central_stack = QStackedWidget()
        self.setCentralWidget(self.central_stack)

        # 1. Login Widget
        from src.ui.login_widget import LoginWidget
        self.login_widget = LoginWidget(self.auth_manager)
        self.login_widget.login_successful.connect(self.on_login_successful)
        self.central_stack.addWidget(self.login_widget)

        # 2. Main App Widget
        self.main_app_widget = QWidget()
        self.setup_main_app_ui()
        self.central_stack.addWidget(self.main_app_widget)

        # Mostrar Login inicialmente
        self.central_stack.setCurrentWidget(self.login_widget)

    def on_login_successful(self, user):
        """Maneja el login exitoso."""
        self.user = user
        self.setWindowTitle(f"Formexa - {self.user['username']}")
        
        # Inicializar páginas ahora que tenemos usuario
        self.init_pages()
        
        self.central_stack.setCurrentWidget(self.main_app_widget)
        
        # Simular click en Home para cargar estado inicial correcto
        if hasattr(self, 'btn_home'):
            self.btn_home.click()

    def setup_main_app_ui(self):
        """Configura la UI principal de la aplicación."""
        # Layout principal (Horizontal: Menú Lateral + Contenido)
        main_layout = QHBoxLayout(self.main_app_widget)
        main_layout.setContentsMargins(0, 0, 20, 0) # Margen derecho para el contenido
        main_layout.setSpacing(20) # Espacio entre menú y contenido

        # Menú Lateral
        self.side_menu = self.create_side_menu()
        main_layout.addWidget(self.side_menu)

        # Área de Contenido (Stacked Widget)
        self.content_area = QStackedWidget()
        main_layout.addWidget(self.content_area)

    # ... (other methods)

    def init_pages(self):
        """Inicializa y añade las páginas al StackedWidget."""
        # Limpiar widgets anteriores si existen
        while self.content_area.count():
            widget = self.content_area.widget(0)
            self.content_area.removeWidget(widget)
            widget.deleteLater()

        self.home_widget = HomeWidget()
        self.calc_widget = CalculatorWidget()
        self.library_widget = LibraryWidget()
        self.inventory_widget = InventoryWidget()
        self.projects_widget = ProjectsWidget(self.auth_manager)
        self.market_widget = MarketplaceWidget()
        self.settings_widget = SettingsWidget()
        
        # Conectar señales
        self.inventory_widget.data_changed.connect(self.home_widget.refresh_dashboard)
        self.settings_widget.logout_requested.connect(self.handle_logout)
        self.settings_widget.exit_requested.connect(self.handle_exit)

        self.content_area.addWidget(self.home_widget)
        self.content_area.addWidget(self.calc_widget)
        self.content_area.addWidget(self.library_widget)
        self.content_area.addWidget(self.inventory_widget)
        self.content_area.addWidget(self.projects_widget)
        self.content_area.addWidget(self.market_widget)
        self.content_area.addWidget(self.settings_widget)

        # Seleccionar página inicial (Esto se hace en on_login_successful)

    def load_styles(self):
        """Carga el archivo QSS."""
        style_path = get_asset_path(os.path.join('assets', 'styles.qss'))
        try:
            with open(style_path, 'r') as f:
                self.setStyleSheet(f.read())
        except FileNotFoundError:
            print(f"No se encontró el archivo de estilos: {style_path}")

    def create_side_menu(self):
        """Crea el panel lateral de navegación."""
        menu_frame = QFrame()
        menu_frame.setObjectName("SideMenu")
        menu_frame.setMinimumWidth(200)
        menu_frame.setMaximumWidth(200) # Mantener fijo pero respetando el mínimo explícito
        
        layout = QVBoxLayout(menu_frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Título / Logo
        logo_label = QLabel()
        
        # Usar ruta absoluta para asegurar que se encuentra la imagen
        logo_path = get_asset_path(os.path.join('assets', 'logo.png'))
        
        logo_pixmap = QPixmap(logo_path)
        if not logo_pixmap.isNull():
            # Escalar el logo proporcionalmente
            scaled_pixmap = logo_pixmap.scaled(180, 180, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(scaled_pixmap)
            logo_label.setAlignment(Qt.AlignCenter)
            logo_label.setStyleSheet("padding: 20px 10px 10px 10px;") # Padding para separar
        else:
            # Fallback a texto si falla la imagen
            logo_label.setText("Formexa")
            logo_label.setAlignment(Qt.AlignCenter)
            logo_label.setStyleSheet("font-size: 20px; font-weight: bold; padding: 20px; color: #b0b0b0;")
        
        layout.addWidget(logo_label)

        # Botones de navegación
        self.btn_home = self.create_menu_button("Inicio", 0)
        self.btn_calc = self.create_menu_button("Calculadora", 1)
        self.btn_library = self.create_menu_button("Biblioteca", 2)
        self.btn_inventory = self.create_menu_button("Inventario", 3)
        self.btn_projects = self.create_menu_button("Proyectos", 4)
        self.btn_market = self.create_menu_button("Marketplace", 5)

        layout.addWidget(self.btn_home)
        layout.addWidget(self.btn_calc)
        layout.addWidget(self.btn_library)
        layout.addWidget(self.btn_inventory)
        layout.addWidget(self.btn_projects)
        layout.addWidget(self.btn_market)
        
        # Configuración
        self.btn_settings = self.create_menu_button("Configuración", 6)
        layout.addWidget(self.btn_settings)
        
        layout.addStretch()
        
        # Versión
        version_label = QLabel("v0.1.0")
        version_label.setAlignment(Qt.AlignCenter)
        version_label.setStyleSheet("color: #666; padding: 10px;")
        layout.addWidget(version_label)

        return menu_frame

    def create_menu_button(self, text, index):
        """Crea un botón del menú lateral."""
        btn = QPushButton(text)
        btn.setObjectName("MenuButton")
        btn.setCheckable(True)
        btn.clicked.connect(lambda: self.switch_page(index, btn))
        return btn


    
    def handle_logout(self):
        """Maneja el cierre de sesión."""
        self.auth_manager.logout()
        self.user = None
        self.setWindowTitle("Formexa")
        self.central_stack.setCurrentWidget(self.login_widget)
        
        # Resetear login widget si es necesario (limpiar campos)
        if hasattr(self.login_widget, 'password_input'):
            self.login_widget.password_input.clear()
    
    def handle_exit(self):
        """Maneja la salida de la aplicación."""
        from PyQt5.QtWidgets import QApplication
        QApplication.quit()

    def switch_page(self, index, button):
        """Cambia la página visible y actualiza el estado de los botones."""
        # Desmarcar todos los botones primero para evitar estados inconsistentes
        for btn in [self.btn_home, self.btn_calc, self.btn_library, self.btn_inventory, 
                   self.btn_projects, self.btn_market, self.btn_settings]:
            btn.setChecked(False)

        # Verificar permisos de invitado
        if self.auth_manager.is_guest():
            # Solo permitir calculadora (index 1) y configuración (index 6)
            if index not in [1, 6]:
                self.show_guest_restriction_message(index)
                # Mantener en calculadora
                self.content_area.setCurrentIndex(1)
                self.btn_calc.setChecked(True)
                return
        
        self.content_area.setCurrentIndex(index)
        
        # Marcar el botón actual
        button.setChecked(True)
    
    def show_guest_restriction_message(self, index):
        """Muestra mensaje informando que la función requiere login."""
        feature_names = {
            0: "Dashboard",
            2: "Biblioteca",
            3: "Inventario",
            4: "Proyectos",
            5: "Marketplace"
        }
        
        feature_name = feature_names.get(index, "esta funcionalidad")
        
        MessageBoxHelper.show_info(self, "Inicio de sesión requerido", 
                                 f"Necesitas iniciar sesión para acceder a {feature_name}.\n\nEl modo invitado solo permite usar la Calculadora de Costes y la Configuración.")
