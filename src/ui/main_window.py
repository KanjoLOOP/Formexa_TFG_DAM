import os
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
from src.ui.customers_widget import CustomersWidget
from src.ui.orders_widget import OrdersWidget
from src.utils.translator import translator

# Page indexes
_IDX_HOME = 0
_IDX_CALC = 1
_IDX_LIBRARY = 2
_IDX_INVENTORY = 3
_IDX_PROJECTS = 4
_IDX_MARKET = 5
_IDX_CUSTOMERS = 6
_IDX_ORDERS = 7
_IDX_SETTINGS = 8

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

        # Conectar traductor después de crear botones
        translator.language_changed.connect(self.retranslate_ui)
        translator.load_saved_language()

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

        # C5c: Pasamos el user_id a los widgets que filtran datos por usuario
        user_id = self.user['id'] if self.user else None

        self.home_widget = HomeWidget(user_id=user_id)
        self.calc_widget = CalculatorWidget()
        self.library_widget = LibraryWidget(user_id=user_id)
        self.inventory_widget = InventoryWidget(user_id=user_id)
        self.projects_widget = ProjectsWidget(self.auth_manager)
        self.market_widget = MarketplaceWidget()
        self.customers_widget = CustomersWidget(user_id=user_id)
        self.orders_widget = OrdersWidget(user_id=user_id)
        self.settings_widget = SettingsWidget()

        # Conectar señales
        self.inventory_widget.data_changed.connect(self.home_widget.refresh_dashboard)
        self.settings_widget.logout_requested.connect(self.handle_logout)
        self.settings_widget.exit_requested.connect(self.handle_exit)

        # Orden debe coincidir con _IDX_* constantes
        self.content_area.addWidget(self.home_widget)        # 0
        self.content_area.addWidget(self.calc_widget)        # 1
        self.content_area.addWidget(self.library_widget)     # 2
        self.content_area.addWidget(self.inventory_widget)   # 3
        self.content_area.addWidget(self.projects_widget)    # 4
        self.content_area.addWidget(self.market_widget)      # 5
        self.content_area.addWidget(self.customers_widget)   # 6
        self.content_area.addWidget(self.orders_widget)      # 7
        self.content_area.addWidget(self.settings_widget)    # 8

    def load_styles(self):
        """Carga el archivo QSS."""
        style_path = get_asset_path(os.path.join('assets', 'styles.qss'))
        try:
            with open(style_path, 'r') as f:
                self.setStyleSheet(f.read())
        except FileNotFoundError:
            from src.utils.logger import logger
            logger.warning(f"No se encontró el archivo de estilos: {style_path}")

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
        tr = translator.tr
        self.btn_home = self.create_menu_button(tr('menu.home'), _IDX_HOME)
        self.btn_calc = self.create_menu_button(tr('menu.calculator'), _IDX_CALC)
        self.btn_library = self.create_menu_button(tr('menu.library'), _IDX_LIBRARY)
        self.btn_inventory = self.create_menu_button(tr('menu.inventory'), _IDX_INVENTORY)
        self.btn_projects = self.create_menu_button(tr('menu.projects'), _IDX_PROJECTS)
        self.btn_market = self.create_menu_button(tr('menu.marketplace'), _IDX_MARKET)
        self.btn_customers = self.create_menu_button(tr('menu.customers'), _IDX_CUSTOMERS)
        self.btn_orders = self.create_menu_button(tr('menu.orders'), _IDX_ORDERS)

        layout.addWidget(self.btn_home)
        layout.addWidget(self.btn_calc)
        layout.addWidget(self.btn_library)
        layout.addWidget(self.btn_inventory)
        layout.addWidget(self.btn_projects)
        layout.addWidget(self.btn_market)
        layout.addWidget(self.btn_customers)
        layout.addWidget(self.btn_orders)

        # Configuración
        self.btn_settings = self.create_menu_button(translator.tr('menu.settings'), _IDX_SETTINGS)
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
        btn.setProperty('menu_index', index)  # Guardar índice para retranslate
        return btn
    
    def retranslate_ui(self):
        """Actualiza todos los textos de la UI con las traducciones."""
        tr = translator.tr
        
        # Título de ventana
        if self.user:
            self.setWindowTitle(f"{tr('app_title')} - {self.user['username']}")
        else:
            self.setWindowTitle(tr('app_title'))
        
        if not hasattr(self, 'btn_home'):
            return

        # Botones de menú
        menu_keys = ['home', 'calculator', 'library', 'inventory', 'projects',
                     'marketplace', 'customers', 'orders', 'settings']
        buttons = [self.btn_home, self.btn_calc, self.btn_library, self.btn_inventory,
                   self.btn_projects, self.btn_market, self.btn_customers,
                   self.btn_orders, self.btn_settings]
        
        for btn, key in zip(buttons, menu_keys):
            btn.setText(tr(f'menu.{key}'))
        
        # Propagar a widgets hijos si existen
        if hasattr(self, 'settings_widget') and self.settings_widget:
            self.settings_widget.retranslate_ui()
        if hasattr(self, 'login_widget') and self.login_widget:
            self.login_widget.retranslate_ui() if hasattr(self.login_widget, 'retranslate_ui') else None


    
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

    def closeEvent(self, event):
        """M11: Pide confirmación antes de cerrar la aplicación."""
        if MessageBoxHelper.ask_confirmation(
            self, 
            "Confirmar salida", 
            "¿Estás seguro de que quieres cerrar Formexa?"
        ):
            event.accept()
        else:
            event.ignore()

    def switch_page(self, index, button):
        """Cambia la página visible y actualiza el estado de los botones."""
        all_btns = [self.btn_home, self.btn_calc, self.btn_library, self.btn_inventory,
                    self.btn_projects, self.btn_market, self.btn_customers,
                    self.btn_orders, self.btn_settings]
        for btn in all_btns:
            btn.setChecked(False)

        # Verificar permisos de invitado
        if self.auth_manager.is_guest():
            if index not in [_IDX_CALC, _IDX_SETTINGS]:
                self.show_guest_restriction_message(index)
                # Mantener en calculadora
                self.content_area.setCurrentIndex(_IDX_CALC)
                self.btn_calc.setChecked(True)
                return
        
        self.content_area.setCurrentIndex(index)
        
        # Marcar el botón actual
        button.setChecked(True)
    
    def show_guest_restriction_message(self, index):
        """Muestra mensaje informando que la función requiere login."""
        feature_names = {
            _IDX_HOME: "Dashboard",
            _IDX_LIBRARY: "Biblioteca",
            _IDX_INVENTORY: "Inventario",
            _IDX_PROJECTS: "Proyectos",
            _IDX_MARKET: "Marketplace",
            _IDX_CUSTOMERS: "Clientes",
            _IDX_ORDERS: "Pedidos",
        }
        
        feature_name = feature_names.get(index, "esta funcionalidad")
        
        MessageBoxHelper.show_info(self, "Inicio de sesión requerido", 
                                 f"Necesitas iniciar sesión para acceder a {feature_name}.\n\nEl modo invitado solo permite usar la Calculadora de Costes y la Configuración.")
