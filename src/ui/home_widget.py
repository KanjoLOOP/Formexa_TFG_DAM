from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QFrame, QGridLayout, QScrollArea)
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from src.logic.inventory_manager import InventoryManager
from src.logic.library_manager import LibraryManager

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
        welcome_label = QLabel("Bienvenido a Gestor 3D")
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
                background-color: #2a2a2a;
                border-radius: 8px;
                border: 1px solid #3a3a3a;
            }
        """)
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Título
        title = QLabel("Inventario de Materiales")
        title.setStyleSheet("font-size: 16px; font-weight: 600; color: #e0e0e0; border: none;")
        layout.addWidget(title)
        
        # Gráfico donut
        self.figure = Figure(figsize=(4, 4), dpi=80, facecolor='#2a2a2a')
        self.canvas = FigureCanvas(self.figure)
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
            
            # Colores discretos en escala de grises
            colors = ['#6a6a6a', '#5a5a5a', '#4a4a4a', '#7a7a7a', '#8a8a8a']
            
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
        panel.setStyleSheet("""
            QFrame {
                background-color: #2a2a2a;
                border-radius: 8px;
                border: 1px solid #3a3a3a;
            }
        """)
        
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
                background-color: #3a3a3a;
                border-radius: 4px;
                padding: 8px;
                margin: 2px 0;
                border: none;
            }
            QFrame:hover {
                background-color: #4a4a4a;
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
        name_label.setStyleSheet("color: #e0e0e0; font-size: 13px; border: none;")
        layout.addWidget(name_label)
        
        layout.addStretch()
        
        return item

    def create_stats_panel(self):
        """Panel con estadísticas rápidas."""
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background-color: #2a2a2a;
                border-radius: 8px;
                border: 1px solid #3a3a3a;
            }
        """)
        
        layout = QHBoxLayout(panel)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Obtener estadísticas
        filaments = self.inventory_manager.get_all_filaments()
        models = self.library_manager.get_all_models()
        
        total_filaments = len(filaments) if filaments else 0
        total_models = len(models) if models else 0
        total_weight = sum(f['weight_current'] for f in filaments) if filaments else 0
        
        # Crear tarjetas de estadísticas
        stats = [
            ("🎨", "Materiales", str(total_filaments)),
            ("📦", "Modelos", str(total_models)),
            ("⚖️", "Stock Total", f"{total_weight:.0f}g")
        ]
        
        for icon, label, value in stats:
            stat_card = self.create_stat_card(icon, label, value)
            layout.addWidget(stat_card)
        
        return panel

    def create_stat_card(self, icon, label, value):
        """Crea una tarjeta de estadística."""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #3a3a3a;
                border-radius: 6px;
                padding: 10px;
                border: none;
            }
        """)
        
        layout = QVBoxLayout(card)
        layout.setAlignment(Qt.AlignCenter)
        
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 32px; border: none;")
        icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label)
        
        value_label = QLabel(value)
        value_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #e0e0e0; border: none;")
        value_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(value_label)
        
        label_text = QLabel(label)
        label_text.setStyleSheet("font-size: 12px; color: #b0b0b0; border: none;")
        label_text.setAlignment(Qt.AlignCenter)
        layout.addWidget(label_text)
        
        return card
