from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QFrame, QGridLayout, QScrollArea, QPushButton, QSizePolicy)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from src.logic.inventory_manager import InventoryManager
from src.logic.library_manager import LibraryManager
from src.ui.notifications_panel import NotificationsPanel


class HomeWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.inventory_manager = InventoryManager()
        self.library_manager = LibraryManager()
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Título de bienvenida
        welcome_label = QLabel("Bienvenido a Formexa")
        welcome_label.setStyleSheet("font-size: 28px; font-weight: bold; color: #b0b0b0; margin-bottom: 10px;")
        main_layout.addWidget(welcome_label)
        
        subtitle = QLabel("Tu centro de control para impresión 3D")
        subtitle.setStyleSheet("font-size: 14px; color: #808080; margin-bottom: 20px;")
        main_layout.addWidget(subtitle)
        
        # Layout horizontal para gráfico y proyectos
        content_layout = QHBoxLayout()
        
        # Panel izquierdo: Gráfico de materiales
        materials_panel = self.create_materials_panel()
        content_layout.addWidget(materials_panel, 1)
        
        # Panel derecho: Últimos proyectos
        projects_panel = self.create_projects_panel()
        content_layout.addWidget(projects_panel, 1)
        
        main_layout.addLayout(content_layout)

        # --- Panel de Notificaciones Inteligentes ---
        self.notifications_panel = NotificationsPanel()
        # Ajustar altura fija para que no ocupe demasiado, o dejar que se expanda según contenido
        self.notifications_panel.setFixedHeight(220) 
        main_layout.addWidget(self.notifications_panel)
        
        self.setLayout(main_layout)



    def create_materials_panel(self):
        """Panel con gráfico de materiales."""
        panel = QFrame()
        panel.setObjectName("Card")
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Título
        title = QLabel("Inventario de Materiales")
        title.setStyleSheet("font-size: 16px; font-weight: 600; color: #e0e0e0; border: none;")
        layout.addWidget(title)
        
        # Gráfico donut
        # Gráfico donut
        self.figure = Figure(figsize=(6, 6), dpi=100, facecolor='#2a2a2a')
        self.figure.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1) # Reducir márgenes
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.ax = self.figure.add_subplot(111)
        
        self.update_materials_chart()
        
        layout.addWidget(self.canvas)
        
        return panel

    def update_materials_chart(self):
        """Actualiza el gráfico de materiales."""
        self.ax.clear()
        
        # Obtener datos de inventario
        filaments = self.inventory_manager.get_all_filaments()
        
        if filaments and len(filaments) > 0:
            # Agrupar por tipo de material
            material_data = {}
            for f in filaments:
                mat_type = f['material_type']
                weight = f['weight_current']
                if mat_type in material_data:
                    material_data[mat_type] += weight
                else:
                    material_data[mat_type] = weight
            
            labels = list(material_data.keys())
            sizes = list(material_data.values())
            
            # Colores discretos en escala de grises y acentos sutiles
            colors = ['#00bcd4', '#0097a7', '#4dd0e1', '#26c6da', '#80deea'] # Tonos Cyan para dark mode
            
            # Crear donut chart
            wedges, texts, autotexts = self.ax.pie(
                sizes, 
                labels=labels, 
                autopct='%1.1f%%',
                startangle=90,
                colors=colors[:len(labels)],
                wedgeprops=dict(width=0.4, edgecolor='#2a2a2a')
            )
            
            # Estilo del texto
            for text in texts:
                text.set_color('#e0e0e0')
                text.set_fontsize(10)
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontsize(9)
                autotext.set_weight('bold')
            
        else:
            # Mensaje si no hay datos
            self.ax.text(0.5, 0.5, 'Sin materiales\nregistrados', 
                        ha='center', va='center', 
                        fontsize=12, color='#808080',
                        transform=self.ax.transAxes)
            self.ax.set_xlim(-1, 1)
            self.ax.set_ylim(-1, 1)
        
        self.ax.axis('equal')
        self.ax.set_facecolor('#2a2a2a')
        self.figure.patch.set_facecolor('#2a2a2a')
        self.canvas.draw()

    def create_projects_panel(self):
        """Panel con últimos proyectos/modelos."""
        panel = QFrame()
        panel.setObjectName("Card")
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Título
        title = QLabel("Últimos Modelos")
        title.setStyleSheet("font-size: 16px; font-weight: 600; color: #e0e0e0; border: none;")
        layout.addWidget(title)
        
        # Obtener últimos modelos
        models = self.library_manager.get_all_models()
        

        if models and len(models) > 0:
            # Mostrar hasta 5 últimos
            for model in models[:5]:
                model_item = self.create_model_item(model['name'])
                layout.addWidget(model_item)
        else:
            no_models = QLabel("No hay modelos registrados")
            no_models.setStyleSheet("color: #808080; padding: 20px; border: none;")
            no_models.setAlignment(Qt.AlignCenter)
            layout.addWidget(no_models)
        
        layout.addStretch()
        
        return panel

    def create_model_item(self, name):
        """Crea un item de modelo."""
        item = QFrame()
        item.setStyleSheet("""
            QFrame {
                background-color: #333333;
                border-radius: 6px;
                padding: 8px;
                margin: 4px 0;
                border: 1px solid #404040;
            }
            QFrame:hover {
                background-color: #404040;
                border: 1px solid #505050;
            }
        """)
        
        layout = QHBoxLayout(item)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # Icono (emoji)
        icon = QLabel("📦")
        icon.setStyleSheet("font-size: 20px; border: none;")
        layout.addWidget(icon)
        
        # Nombre
        name_label = QLabel(name)
        name_label.setStyleSheet("color: #e0e0e0; font-size: 14px; font-weight: 500; border: none;")
        layout.addWidget(name_label)
        
        layout.addStretch()
        
        # Botón de acción (simulado)
        btn_open = QPushButton("Abrir")
        btn_open.setCursor(Qt.PointingHandCursor)
        btn_open.setStyleSheet("""
            QPushButton {
                background-color: #00bcd4;
                color: #000000;
                border-radius: 4px;
                padding: 4px 12px;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover {
                background-color: #26c6da;
            }
        """)
        layout.addWidget(btn_open)
        
        layout.addStretch()
        
        return item

    def refresh_dashboard(self):
        """Actualiza todos los elementos del dashboard."""
        self.update_materials_chart()
        if hasattr(self, 'notifications_panel'):
            self.notifications_panel.refresh_data()


