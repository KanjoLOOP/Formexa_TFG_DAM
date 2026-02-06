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
        welcome_label.setAlignment(Qt.AlignCenter)
        welcome_label.setStyleSheet("font-size: 28px; font-weight: bold; color: #b0b0b0; margin-bottom: 5px;")
        main_layout.addWidget(welcome_label)
        
        subtitle = QLabel("Tu centro de control para impresión 3D")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("font-size: 14px; color: #808080; margin-bottom: 25px;")
        main_layout.addWidget(subtitle)
        
        # Layout horizontal para gráfico y proyectos
        content_layout = QHBoxLayout()
        
        # Panel izquierdo: Gráfico de materiales
        materials_panel = self.create_materials_panel()
        content_layout.addWidget(materials_panel, 1)
        
        # Panel derecho: Últimos proyectos
        # Panel derecho: Inventario por Color
        colors_panel = self.create_colors_panel()
        content_layout.addWidget(colors_panel, 1)
        
        main_layout.addLayout(content_layout)

        # --- Panel de Notificaciones Inteligentes ---
        self.notifications_panel = NotificationsPanel()
        # Ajustar altura fija para que no ocupe demasiado, o dejar que se expanda según contenido
        self.notifications_panel.setFixedHeight(220) 
        main_layout.addWidget(self.notifications_panel)
        
        self.setLayout(main_layout)

    def get_hex_for_color_name(self, color_name):
        """Convierte nombres de colores comunes a HEX realistas para filamentos."""
        if not color_name:
            return "#808080" # Gris por defecto
            
        c = color_name.lower().strip()
        
        mapping = {
            'negro': '#212121', 'black': '#212121',
            'blanco': '#f5f5f5', 'white': '#f5f5f5',
            'grs': '#9e9e9e', 'grey': '#9e9e9e', 'gris': '#9e9e9e', 'silver': '#c0c0c0', 'plateado': '#c0c0c0',
            'rojo': '#d32f2f', 'red': '#d32f2f',
            'azul': '#1976d2', 'blue': '#1976d2',
            'verde': '#388e3c', 'green': '#388e3c',
            'amarillo': '#fbc02d', 'yellow': '#fbc02d',
            'naranja': '#f57c00', 'orange': '#f57c00',
            'morado': '#7b1fa2', 'purple': '#7b1fa2', 'violeta': '#7b1fa2',
            'rosa': '#e91e63', 'pink': '#e91e63',
            'marrón': '#795548', 'brown': '#795548', 'marron': '#795548',
            'transparente': '#e0f7fa', 'transparent': '#e0f7fa', 'natural': '#fff9c4',
            'oro': '#ffd700', 'gold': '#ffd700', 'dorado': '#ffd700',
            'cobre': '#bcaaa4', 'copper': '#bcaaa4',
            'bronce': '#cd7f32', 'bronze': '#cd7f32'
        }
        
        for key in mapping:
            if key in c:
                return mapping[key]
                
        return "#b0bec5" # Gris azulado por defecto si no encuentra



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
        # self.figure.subplots_adjust(left=0.05, right=0.75, top=0.95, bottom=0.05) # Ajuste movido a update_materials_chart
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.ax = self.figure.add_subplot(111)
        
        self.update_materials_chart()
        
        layout.addWidget(self.canvas)
        
        return panel

    def update_materials_chart(self):
        """Actualiza el gráfico con un diseño simplificado: Cantidad por Material."""
        self.ax.clear()
        
        filaments = self.inventory_manager.get_all_filaments()
        
        if filaments and len(filaments) > 0:
            # 1. Agregación de Datos por TIPO
            data_map = {}
            for f in filaments:
                mat_type = f['material_type'].upper().strip()
                weight = f['weight_current']
                data_map[mat_type] = data_map.get(mat_type, 0.0) + weight
            
            total_weight = sum(data_map.values())
            
            # 2. Filtrado y Agrupación "Otros"
            # Criterio: < 5% del total
            threshold = 0.05 * total_weight
            
            final_data = {}
            other_weight = 0.0
            
            for m_type, w in data_map.items():
                if w >= threshold:
                    final_data[m_type] = w
                else:
                    other_weight += w
            
            if other_weight > 0:
                final_data['OTROS'] = other_weight
                
            # 3. Ordenación (Mayor a Menor)
            # Convertir a lista de tuplas para ordenar
            sorted_items = sorted(final_data.items(), key=lambda x: x[1], reverse=True)
            
            labels = [item[0] for item in sorted_items]
            sizes = [item[1] for item in sorted_items]
            
            # 4. Paleta de Colores Coherente
            # Frios: PLA, PETG
            # Calidos: ABS, ASA, TPU, NYLON, PC
            # Neutro: OTROS
            
            palette_map = {
                'PLA': '#0288d1',   # Azul Claro
                'PLA+': '#039be5',  # Azul Intenso
                'PETG': '#0097a7',  # Cyan / Teal
                
                'ABS': '#d32f2f',   # Rojo
                'ASA': '#f57c00',   # Naranja
                'TPU': '#fbc02d',   # Amarillo
                'NYLON': '#5d4037', # Marrón
                'PC': '#616161',    # Gris Oscuro
                
                'OTROS': '#9e9e9e'  # Gris Medio
            }
            
            colors = []
            default_colors = ['#78909c', '#546e7a', '#455a64', '#37474f'] # Fallback
            
            for i, label in enumerate(labels):
                c = palette_map.get(label)
                if not c:
                     # Fallback si no está mapeado explícitamente
                     c = default_colors[i % len(default_colors)]
                colors.append(c)
                
            # 5. Plotting (Donut Simple)
            # startangle=90 con orden descendente empieza a las 12 en sentido antihorario (por defecto matplotlib)
            # Para que vaya en sentido horario desde las 12, usamos counterclock=False, startangle=90
            
            wedges, _ = self.ax.pie(
                sizes,
                labels=None,
                colors=colors,
                startangle=90,
                counterclock=False,
                wedgeprops=dict(width=0.35, edgecolor='#1e1e1e', linewidth=2) # Anillo no muy grueso
            )
            
            # Texto Central (Total)
            self.ax.text(0.0, 0.0, f"{total_weight/1000:.1f} kg\nTotal", 
                         ha='center', va='center', fontsize=14, fontweight='bold', color='#e0e0e0')
            
            # 6. Leyenda Simplificada
            # "Material - XX%"
            legend_labels = []
            for lab, siz in zip(labels, sizes):
                pct = (siz / total_weight) * 100
                legend_labels.append(f"{lab} ({pct:.1f}%)")
                
            # Leyenda inferior centrada
            legend = self.ax.legend(
                wedges,
                legend_labels,
                loc="upper center",
                bbox_to_anchor=(0.5, -0.05),
                frameon=False,
                ncol=2,
                labelcolor='#b0bec5',
                fontsize=10
            )
            
        else:
            self.ax.text(0.5, 0.5, '0.0 kg\nSin Stock', 
                        ha='center', va='center', 
                        fontsize=12, color='#546e7a',
                        transform=self.ax.transAxes)
            self.ax.set_xlim(-1, 1)
            self.ax.set_ylim(-1, 1)        
        
        self.ax.axis('equal')
        self.ax.set_facecolor('#2a2a2a') 
        self.figure.patch.set_facecolor('#1e1e1e')
        
        # Márgenes limpios
        self.figure.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.25)
        
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


    def update_colors_chart(self):
        """Actualiza el gráfico de Colores: Cantidad por Color."""
        if not hasattr(self, 'ax_colors'):
            return

        self.ax_colors.clear()
        
        filaments = self.inventory_manager.get_all_filaments()
        
        if filaments and len(filaments) > 0:
            # 1. Agregación de Datos por COLOR
            data_map = {}
            for f in filaments:
                color_raw = f['color']
                if not color_raw:
                    color_raw = "Desconocido"
                c_name = color_raw.strip().title()
                weight = f['weight_current']
                data_map[c_name] = data_map.get(c_name, 0.0) + weight
            
            total_weight = sum(data_map.values())
            
            # 2. Filtrado (< 5%)
            threshold = 0.05 * total_weight
            final_data = {}
            other_weight = 0.0
            
            for c_name, w in data_map.items():
                if w >= threshold:
                    final_data[c_name] = w
                else:
                    other_weight += w
            
            if other_weight > 0:
                final_data['Otros'] = other_weight
                
            # 3. Ordenar
            sorted_items = sorted(final_data.items(), key=lambda x: x[1], reverse=True)
            labels = [item[0] for item in sorted_items]
            sizes = [item[1] for item in sorted_items]
            
            # 4. Paleta
            colors = []
            for lab in labels:
                if lab == 'Otros':
                    colors.append('#9e9e9e')
                else:
                    colors.append(self.get_hex_for_color_name(lab))
            
            # 5. Plotting
            wedges, _ = self.ax_colors.pie(
                sizes,
                labels=None,
                colors=colors,
                startangle=90,
                counterclock=False,
                wedgeprops=dict(width=0.35, edgecolor='#1e1e1e', linewidth=2)
            )
            
            # Texto Central
            self.ax_colors.text(0.0, 0.0, f"{total_weight/1000:.1f} kg\nTotal", 
                         ha='center', va='center', fontsize=14, fontweight='bold', color='#e0e0e0')
            
            # 6. Leyenda
            legend_labels = []
            for lab, siz in zip(labels, sizes):
                pct = (siz / total_weight) * 100
                legend_labels.append(f"{lab} ({pct:.1f}%)")
                
            self.ax_colors.legend(
                wedges,
                legend_labels,
                loc="upper center",
                bbox_to_anchor=(0.5, -0.05),
                frameon=False,
                ncol=2,
                labelcolor='#b0bec5',
                fontsize=9
            )
            
        else:
            self.ax_colors.text(0.5, 0.5, '0.0 kg\nSin Colores', 
                        ha='center', va='center', 
                        fontsize=12, color='#546e7a',
                        transform=self.ax_colors.transAxes)
            self.ax_colors.set_xlim(-1, 1)
            self.ax_colors.set_ylim(-1, 1)        
        
        self.ax_colors.axis('equal')
        self.ax_colors.set_facecolor('#2a2a2a') 
        self.figure_colors.patch.set_facecolor('#1e1e1e')
        self.figure_colors.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.25)
        self.canvas_colors.draw()

    def create_colors_panel(self):
        """Panel con gráfico de inventario por Colores."""
        panel = QFrame()
        panel.setObjectName("Card")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Título
        title = QLabel("Inventario por Color")
        title.setStyleSheet("font-size: 16px; font-weight: 600; color: #e0e0e0; border: none;")
        layout.addWidget(title)
        
        # Gráfico donut
        self.figure_colors = Figure(figsize=(6, 6), dpi=100, facecolor='#2a2a2a')
        self.canvas_colors = FigureCanvas(self.figure_colors)
        self.canvas_colors.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.ax_colors = self.figure_colors.add_subplot(111)
        
        self.update_colors_chart()
        layout.addWidget(self.canvas_colors)
        
        return panel

    def refresh_dashboard(self):
        """Actualiza todos los elementos del dashboard."""
        self.update_materials_chart()
        self.update_colors_chart()
        if hasattr(self, 'notifications_panel'):
            self.notifications_panel.refresh_data()


