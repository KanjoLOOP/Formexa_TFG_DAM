from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QProgressBar)
from PyQt5.QtCore import Qt
from src.logic.inventory_manager import InventoryManager
from src.logic.library_manager import LibraryManager
from src.logic.project_manager import ProjectManager

class NotificationsPanel(QWidget):
    def __init__(self, user_id=None):
        super().__init__()
        # C5c / M8: user_id para filtrar datos y mostrar estadísticas reales
        self.user_id = user_id
        self.inventory_manager = InventoryManager()
        self.library_manager = LibraryManager()
        self.project_manager = ProjectManager()  # M8: para estadísticas reales
        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Tarjeta 1: Filamentos con poco material
        self.low_material_card = self.create_card("Filamentos con poco material")
        self.populate_low_material_card(self.low_material_card)
        main_layout.addWidget(self.low_material_card)

        # Tarjeta 2: Filamentos más usados este mes
        self.most_used_card = self.create_card("Filamentos más usados este mes")
        self.populate_most_used_card(self.most_used_card)
        main_layout.addWidget(self.most_used_card)

        # Tarjeta 3: Resumen mensual
        self.monthly_summary_card = self.create_card("Resumen mensual")
        self.populate_monthly_summary_card(self.monthly_summary_card)
        main_layout.addWidget(self.monthly_summary_card)

        self.setLayout(main_layout)

    def create_card(self, title_text):
        """Crea una tarjeta base con estilo unificado."""
        card = QFrame()
        card.setObjectName("Card") # Usa el estilo definido en styles.qss
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        title = QLabel(title_text)
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #e0e0e0; border: none; margin-bottom: 5px;")
        layout.addWidget(title)

        return card

    def populate_low_material_card(self, card):
        layout = card.layout()
        
        # Lógica para obtener filamentos bajos
        # C5c: Filtramos filamentos por usuario
        filaments = self.inventory_manager.get_all_filaments(self.user_id)
        low_stock_filaments = []

        for f in filaments:
            try:
                initial = float(f['weight_initial'])
                current = float(f['weight_current'])
                if initial > 0:
                    percentage = (current / initial) * 100
                    if percentage < 20:
                        low_stock_filaments.append({
                            'name': f"{f['brand']} {f['material_type']} {f['color']}",
                            'current': current,
                            'percentage': percentage
                        })
            except (ValueError, KeyError):
                continue
        
        if not low_stock_filaments:
            lbl = QLabel("No hay alertas de material")
            lbl.setStyleSheet("color: #808080; font-style: italic; border: none;")
            lbl.setAlignment(Qt.AlignCenter)
            layout.addWidget(lbl)
            layout.addStretch()
            return

        # Mostrar alertas (máximo 3 para no saturar)
        for item in low_stock_filaments[:3]:
            item_widget = QWidget()
            item_layout = QVBoxLayout(item_widget)
            item_layout.setContentsMargins(0, 5, 0, 5)
            item_layout.setSpacing(2)

            # Nombre y Peso
            header_layout = QHBoxLayout()
            name_lbl = QLabel(item['name'])
            name_lbl.setStyleSheet("color: #e0e0e0; font-weight: 500; border: none;")
            weight_lbl = QLabel(f"{item['current']:.0f}g")
            weight_lbl.setStyleSheet("color: #b0b0b0; border: none;")
            
            header_layout.addWidget(name_lbl)
            header_layout.addStretch()
            header_layout.addWidget(weight_lbl)
            item_layout.addLayout(header_layout)

            # Barra de progreso
            progress = QProgressBar()
            progress.setRange(0, 100)
            progress.setValue(int(item['percentage']))
            progress.setTextVisible(False)
            progress.setFixedHeight(6)
            
            # Color según criticidad
            color = "#f44336" if item['percentage'] < 10 else "#ff9800" # Rojo (<10%) o Amarillo (10-20%)
            progress.setStyleSheet(f"""
                QProgressBar {{
                    border: none;
                    background-color: #404040;
                    border-radius: 3px;
                }}
                QProgressBar::chunk {{
                    background-color: {color};
                    border-radius: 3px;
                }}
            """)
            item_layout.addWidget(progress)
            
            layout.addWidget(item_widget)
        
        layout.addStretch()

    def populate_most_used_card(self, card):
        layout = card.layout()
        
        # Mock data (ya que no hay historial de uso real en BD aún)
        # En una implementación real, esto vendría de una tabla 'print_jobs' o similar
        most_used = [] 
        # Ejemplo de estructura: [{'name': 'PLA Negro', 'amount': '850g', 'percent': 80}, ...]

        if not most_used:
            lbl = QLabel("Sin datos de uso aún")
            lbl.setStyleSheet("color: #808080; font-style: italic; border: none;")
            lbl.setAlignment(Qt.AlignCenter)
            layout.addWidget(lbl)
            layout.addStretch()
            return

        for item in most_used[:3]:
            item_widget = QWidget()
            item_layout = QVBoxLayout(item_widget)
            item_layout.setContentsMargins(0, 5, 0, 5)
            
            header_layout = QHBoxLayout()
            name_lbl = QLabel(item['name'])
            name_lbl.setStyleSheet("color: #e0e0e0; border: none;")
            amount_lbl = QLabel(item['amount'])
            amount_lbl.setStyleSheet("color: #b0b0b0; border: none;")
            
            header_layout.addWidget(name_lbl)
            header_layout.addStretch()
            header_layout.addWidget(amount_lbl)
            item_layout.addLayout(header_layout)

            # Barra simple
            bar = QFrame()
            bar.setFixedHeight(4)
            bar.setStyleSheet(f"""
                background-color: #404040;
                border-radius: 2px;
            """)
            # Simular llenado con un layout interno o gradiente (aquí simple frame gris por ahora si no hay % real)
            # Para hacerlo bien visualmente necesitaríamos un frame interno con ancho variable
            
            fill = QFrame(bar)
            fill.setStyleSheet("background-color: #00bcd4; border-radius: 2px;")
            fill.setGeometry(0, 0, int(item['percent'] * 2), 4) # Ancho simulado relativo

            item_layout.addWidget(bar)
            layout.addWidget(item_widget)

        layout.addStretch()

    def populate_monthly_summary_card(self, card):
        layout = card.layout()
        
        # M8: Mostrar estadísticas reales del usuario si está logueado
        if self.user_id and self.user_id != -1:
            stats = self.project_manager.get_project_stats(self.user_id)
            # stats es un Row de sqlite3 — accedemos por índice
            if stats and stats[0]:  # stats[0] = total_projects
                total_projects = stats[0] or 0
                total_spent = stats[4] or 0.0  # stats[4] = total_spent
                total_hours = stats[5] or 0.0  # stats[5] = total_hours
                
                projects_lbl = QLabel(f"Proyectos: {total_projects}")
                projects_lbl.setStyleSheet("color: #e0e0e0; font-size: 13px; border: none;")
                layout.addWidget(projects_lbl)
                
                cost_lbl = QLabel(f"Gasto total: {total_spent:.2f} €")
                cost_lbl.setStyleSheet("color: #28a745; font-size: 13px; font-weight: bold; border: none;")
                layout.addWidget(cost_lbl)
                
                hours_lbl = QLabel(f"Horas impresas: {total_hours:.1f} h")
                hours_lbl.setStyleSheet("color: #b0b0b0; font-size: 13px; border: none;")
                layout.addWidget(hours_lbl)
            else:
                # Sin proyectos creados aún
                no_data_lbl = QLabel("Aún no tienes proyectos")
                no_data_lbl.setStyleSheet("color: #808080; font-style: italic; border: none;")
                no_data_lbl.setAlignment(Qt.AlignCenter)
                layout.addWidget(no_data_lbl)
        else:
            # Usuario invitado o sin sesión — mostrar datos mock
            top_material_lbl = QLabel("Material Top: --")
            top_material_lbl.setStyleSheet("color: #b0b0b0; font-size: 13px; border: none;")
            layout.addWidget(top_material_lbl)
            
            cost_lbl = QLabel("Gasto est.: 0.00 €")
            cost_lbl.setStyleSheet("color: #b0b0b0; font-size: 13px; border: none;")
            layout.addWidget(cost_lbl)

        # Separador
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("background-color: #404040; border: none; max-height: 1px; margin: 5px 0;")
        layout.addWidget(line)

        # Últimos modelos añadidos (C5c: filtrado por usuario)
        models = self.library_manager.get_all_models(self.user_id if self.user_id and self.user_id != -1 else None)
        
        recent_lbl = QLabel("Añadidos recientemente:")
        recent_lbl.setStyleSheet("color: #e0e0e0; font-weight: bold; font-size: 13px; border: none; margin-top: 5px;")
        layout.addWidget(recent_lbl)

        if not models:
            lbl = QLabel("No hay modelos recientes")
            lbl.setStyleSheet("color: #808080; font-style: italic; font-size: 12px; border: none;")
            layout.addWidget(lbl)
        else:
            for model in models[:3]:
                m_lbl = QLabel(f"• {model['name']}")
                m_lbl.setStyleSheet("color: #b0b0b0; font-size: 12px; border: none;")
                layout.addWidget(m_lbl)

        layout.addStretch()

    def refresh_data(self):
        """Actualiza los datos de todas las tarjetas."""
        # Limpiar layouts de tarjetas (excepto título)
        for card, populate_func in [
            (self.low_material_card, self.populate_low_material_card),
            (self.most_used_card, self.populate_most_used_card),
            (self.monthly_summary_card, self.populate_monthly_summary_card)
        ]:
            layout = card.layout()
            # Eliminar todo menos el título (index 0)
            while layout.count() > 1:
                item = layout.takeAt(1)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
                else:
                    # Si es un layout anidado o spacer
                    pass
            
            # Repoblar
            populate_func(card)
