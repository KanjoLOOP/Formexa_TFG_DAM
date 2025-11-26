import os
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QStackedWidget, QFrame, QLabel)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

from src.ui.home_widget import HomeWidget
from src.ui.calculator_widget import CalculatorWidget
from src.ui.library_widget import LibraryWidget
from src.ui.inventory_widget import InventoryWidget
from src.ui.marketplace_widget import MarketplaceWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestor 3D")
        self.resize(1100, 750)
        
        # Cargar estilos
        self.load_styles()

        # Widget central principal
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal (Horizontal: Menú Lateral + Contenido)
        # Layout principal (Horizontal: Menú Lateral + Contenido)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 20, 0) # Margen derecho para el contenido
        main_layout.setSpacing(20) # Espacio entre menú y contenido

        # Menú Lateral
        self.side_menu = self.create_side_menu()
        main_layout.addWidget(self.side_menu)

        # Área de Contenido (Stacked Widget)
        self.content_area = QStackedWidget()
        main_layout.addWidget(self.content_area)

        # Inicializar páginas
        self.init_pages()

    def load_styles(self):
        """Carga el archivo QSS."""
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        style_path = os.path.join(base_path, 'assets', 'styles.qss')
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
        title_label = QLabel("Gestor 3D")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; padding: 20px; color: #b0b0b0;")
        layout.addWidget(title_label)

        # Botones de navegación
        self.btn_home = self.create_menu_button("Inicio", 0)
        self.btn_calc = self.create_menu_button("Calculadora", 1)
        self.btn_library = self.create_menu_button("Biblioteca", 2)
        self.btn_inventory = self.create_menu_button("Inventario", 3)
        self.btn_market = self.create_menu_button("Marketplace", 4)

        layout.addWidget(self.btn_home)
        layout.addWidget(self.btn_calc)
        layout.addWidget(self.btn_library)
        layout.addWidget(self.btn_inventory)
        layout.addWidget(self.btn_market)
        
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

    def init_pages(self):
        """Inicializa y añade las páginas al StackedWidget."""
        self.home_widget = HomeWidget()
        self.calc_widget = CalculatorWidget()
        self.library_widget = LibraryWidget()
        self.inventory_widget = InventoryWidget()
        self.market_widget = MarketplaceWidget()

        self.content_area.addWidget(self.home_widget)
        self.content_area.addWidget(self.calc_widget)
        self.content_area.addWidget(self.library_widget)
        self.content_area.addWidget(self.inventory_widget)
        self.content_area.addWidget(self.market_widget)

        # Seleccionar página inicial
        self.btn_home.click()

    def switch_page(self, index, button):
        """Cambia la página visible y actualiza el estado de los botones."""
        self.content_area.setCurrentIndex(index)
        
        # Desmarcar todos los botones
        for btn in [self.btn_home, self.btn_calc, self.btn_library, self.btn_inventory, self.btn_market]:
            btn.setChecked(False)
        
        # Marcar el botón actual
        button.setChecked(True)
