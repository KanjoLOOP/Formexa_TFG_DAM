from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
                             QPushButton, QScrollArea, QFrame, QMessageBox, QDialog,
                             QFormLayout, QLineEdit, QComboBox, QTextEdit, QDoubleSpinBox,
                             QFileDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from src.logic.project_manager import ProjectManager
from src.logic.library_manager import LibraryManager
from src.logic.inventory_manager import InventoryManager
from src.logic.report_generator import ReportGenerator

class ProjectsWidget(QWidget):
    """Widget para gestión de proyectos de impresión 3D."""
    
    def __init__(self, auth_manager):
        super().__init__()
        self.auth_manager = auth_manager
        self.user = auth_manager.get_current_user()
        self.project_manager = ProjectManager()
        self.library_manager = LibraryManager()
        self.inventory_manager = InventoryManager()
        self.report_generator = ReportGenerator()
        self.init_ui()
    
    def init_ui(self):
        self.setStyleSheet("background-color: #1E1E1E;")
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("Mis Proyectos")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: white;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Botón exportar estadísticas
        btn_stats = QPushButton("Exportar Estadísticas")
        btn_stats.setCursor(Qt.PointingHandCursor)
        btn_stats.setStyleSheet("""
            QPushButton {
                background-color: #2C3E50;
                color: white;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #34495E;
            }
        """)
        btn_stats.clicked.connect(self.export_stats)
        header_layout.addWidget(btn_stats)
        
        # Botón nuevo proyecto
        btn_new = QPushButton("+ Nuevo Proyecto")
        btn_new.setCursor(Qt.PointingHandCursor)
        btn_new.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        btn_new.clicked.connect(self.open_new_project_dialog)
        header_layout.addWidget(btn_new)
        
        layout.addLayout(header_layout)
        
        # Área de scroll para proyectos
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background-color: transparent;")
        
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background-color: transparent;")
        self.projects_layout = QGridLayout(scroll_content)
        self.projects_layout.setSpacing(20)
        self.projects_layout.setContentsMargins(0, 0, 0, 0)
        
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        
        self.setLayout(layout)
        
        # Cargar proyectos
        self.load_projects()
    
    def load_projects(self):
        """Carga y muestra todos los proyectos del usuario."""
        # Limpiar layout
        for i in reversed(range(self.projects_layout.count())):
            widget = self.projects_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        
        # Obtener proyectos
        projects = self.project_manager.get_all_projects(self.user['id'])
        
        if not projects:
            # Mensaje si no hay proyectos
            no_projects = QLabel("No tienes proyectos aún. ¡Crea tu primer proyecto!")
            no_projects.setStyleSheet("color: #888; font-size: 16px; padding: 40px;")
            no_projects.setAlignment(Qt.AlignCenter)
            self.projects_layout.addWidget(no_projects, 0, 0)
            return
        
        # Mostrar proyectos en grid
        col_count = 3
        for i, project in enumerate(projects):
            card = self.create_project_card(project)
            row = i // col_count
            col = i % col_count
            self.projects_layout.addWidget(card, row, col)
    
    def create_project_card(self, project):
        """Crea una tarjeta de proyecto."""
        card = QFrame()
        card.setObjectName("Card")
        card.setFixedSize(320, 240)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        
        # Nombre del proyecto
        name = QLabel(project[1])  # name
        name.setStyleSheet("font-size: 18px; font-weight: bold; color: white;")
        name.setWordWrap(True)
        layout.addWidget(name)
        
        # Estado
        status = project[3]  # status
        status_label = QLabel(f"Estado: {status}")
        status_colors = {
            'Pendiente': '#FFA500',
            'En Progreso': '#007BFF',
            'Completado': '#28a745'
        }
        color = status_colors.get(status, '#888')
        status_label.setStyleSheet(f"color: {color}; font-weight: bold;")
        layout.addWidget(status_label)
        
        # Modelo y filamento
        model_name = project[11] if project[11] else "Sin modelo"
        filament_info = f"{project[12]} {project[13]}" if project[12] else "Sin filamento"
        
        info = QLabel(f"Modelo: {model_name}\nFilamento: {filament_info}")
        info.setStyleSheet("color: #aaa; font-size: 12px;")
        info.setWordWrap(True)
        layout.addWidget(info)
        
        # Coste total
        total_cost = project[6] if project[6] else 0
        cost_label = QLabel(f"Coste: {total_cost:.2f} €")
        cost_label.setStyleSheet("color: #28a745; font-size: 16px; font-weight: bold;")
        layout.addWidget(cost_label)
        
        layout.addStretch()
        
        # Botones de acción
        btn_layout = QHBoxLayout()
        
        btn_edit = QPushButton("Editar")
        btn_edit.setCursor(Qt.PointingHandCursor)
        btn_edit.setStyleSheet("""
            QPushButton {
                background-color: #007BFF;
                color: white;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        btn_edit.clicked.connect(lambda: self.edit_project(project[0]))
        btn_layout.addWidget(btn_edit)
        
        btn_delete = QPushButton("Eliminar")
        btn_delete.setCursor(Qt.PointingHandCursor)
        btn_delete.setStyleSheet("""
            QPushButton {
                background-color: #1E1E1E;
                color: #dc3545;
                border: 1px solid #dc3545;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #dc3545;
                color: white;
            }
        """)
        btn_delete.clicked.connect(lambda: self.delete_project(project[0], project[1]))
        btn_layout.addWidget(btn_delete)
        
        layout.addLayout(btn_layout)
        
        return card
    
    def open_new_project_dialog(self):
        """Abre el diálogo para crear un nuevo proyecto."""
        dialog = ProjectDialog(self, self.user['id'], self.library_manager, self.inventory_manager)
        if dialog.exec_() == QDialog.Accepted:
            self.load_projects()
    
    def edit_project(self, project_id):
        """Abre el diálogo para editar un proyecto."""
        project = self.project_manager.get_project_by_id(project_id)
        if project:
            dialog = ProjectDialog(self, self.user['id'], self.library_manager, 
                                  self.inventory_manager, project)
            if dialog.exec_() == QDialog.Accepted:
                self.load_projects()
    
    def delete_project(self, project_id, project_name):
        """Elimina un proyecto."""
        msg_box = QMessageBox(self.window())
        msg_box.setWindowTitle("Confirmar eliminación")
        msg_box.setText(f"¿Estás seguro de que deseas eliminar el proyecto '{project_name}'?")
        msg_box.setIcon(QMessageBox.Question)
        btn_yes = msg_box.addButton("Sí", QMessageBox.YesRole)
        btn_no = msg_box.addButton("No", QMessageBox.NoRole)
        msg_box.exec_()
        
        if msg_box.clickedButton() == btn_yes:
            success, message = self.project_manager.delete_project(project_id)
            
            msg_result = QMessageBox(self.window())
            msg_result.setWindowTitle("Éxito" if success else "Error")
            msg_result.setText(message)
            msg_result.setIcon(QMessageBox.Information if success else QMessageBox.Warning)
            msg_result.addButton("Aceptar", QMessageBox.AcceptRole)
            msg_result.exec_()
            
            if success:
                self.load_projects()

    def export_stats(self):
        """Exporta las estadísticas de proyectos a PDF."""
        stats = self.project_manager.get_project_stats(self.user['id'])
        
        if not stats or stats['total_projects'] == 0:
            QMessageBox.warning(self, "Aviso", "No hay datos suficientes para generar un informe.")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Guardar Informe de Estadísticas", "", "Archivos PDF (*.pdf)"
        )
        
        if file_path:
            if not file_path.endswith('.pdf'):
                file_path += '.pdf'
                
            try:
                # Convertir Row a dict si es necesario
                stats_dict = dict(stats)
                self.report_generator.generate_stats_report(self.user['username'], stats_dict, file_path)
                QMessageBox.information(self, "Éxito", "Informe guardado correctamente")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"No se pudo guardar el informe: {str(e)}")


class ProjectDialog(QDialog):
    """Diálogo para crear/editar proyectos."""
    
    def __init__(self, parent, user_id, library_manager, inventory_manager, project=None):
        super().__init__(parent)
        self.user_id = user_id
        self.library_manager = library_manager
        self.inventory_manager = inventory_manager
        self.project_manager = ProjectManager()
        self.project = project
        self.is_edit = project is not None
        
        self.setWindowTitle("Editar Proyecto" if self.is_edit else "Nuevo Proyecto")
        self.setMinimumSize(500, 600)
        self.setStyleSheet("background-color: #2C2C2C; color: white;")
        
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        
        # Nombre
        self.name_input = QLineEdit()
        self.name_input.setStyleSheet(self.get_input_style())
        if self.is_edit:
            self.name_input.setText(self.project[1])
        form_layout.addRow("Nombre:", self.name_input)
        
        # Descripción
        self.desc_input = QTextEdit()
        self.desc_input.setMaximumHeight(80)
        self.desc_input.setStyleSheet(self.get_input_style())
        if self.is_edit and self.project[2]:
            self.desc_input.setPlainText(self.project[2])
        form_layout.addRow("Descripción:", self.desc_input)
        
        # Estado
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Pendiente", "En Progreso", "Completado"])
        self.status_combo.setStyleSheet(self.get_combo_style())
        if self.is_edit:
            index = self.status_combo.findText(self.project[3])
            if index >= 0:
                self.status_combo.setCurrentIndex(index)
        form_layout.addRow("Estado:", self.status_combo)
        
        # Modelo
        self.model_combo = QComboBox()
        self.load_models()
        self.model_combo.setStyleSheet(self.get_combo_style())
        if self.is_edit and self.project[9]:
            index = self.model_combo.findData(self.project[9])
            if index >= 0:
                self.model_combo.setCurrentIndex(index)
        form_layout.addRow("Modelo:", self.model_combo)
        
        # Filamento
        self.filament_combo = QComboBox()
        self.load_filaments()
        self.filament_combo.setStyleSheet(self.get_combo_style())
        if self.is_edit and self.project[10]:
            index = self.filament_combo.findData(self.project[10])
            if index >= 0:
                self.filament_combo.setCurrentIndex(index)
        form_layout.addRow("Filamento:", self.filament_combo)
        
        # Peso
        self.weight_input = QDoubleSpinBox()
        self.weight_input.setRange(0, 10000)
        self.weight_input.setSuffix(" g")
        self.weight_input.setStyleSheet(self.get_input_style())
        if self.is_edit and self.project[4]:
            self.weight_input.setValue(self.project[4])
        form_layout.addRow("Peso:", self.weight_input)
        
        # Tiempo de impresión
        self.time_input = QDoubleSpinBox()
        self.time_input.setRange(0, 1000)
        self.time_input.setSuffix(" h")
        self.time_input.setDecimals(1)
        self.time_input.setStyleSheet(self.get_input_style())
        if self.is_edit and self.project[5]:
            self.time_input.setValue(self.project[5])
        form_layout.addRow("Tiempo impresión:", self.time_input)
        
        layout.addLayout(form_layout)
        
        # Botones
        btn_layout = QHBoxLayout()
        
        btn_save = QPushButton("Guardar")
        btn_save.setCursor(Qt.PointingHandCursor)
        btn_save.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border-radius: 4px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        btn_save.clicked.connect(self.save_project)
        btn_layout.addWidget(btn_save)
        
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setCursor(Qt.PointingHandCursor)
        btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border-radius: 4px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)
    
    def load_models(self):
        """Carga los modelos disponibles."""
        self.model_combo.addItem("Sin modelo", None)
        models = self.library_manager.get_all_models()
        for model in models:
            # model es un diccionario o Row
            self.model_combo.addItem(model['name'], model['id'])
    
    def load_filaments(self):
        """Carga los filamentos disponibles."""
        self.filament_combo.addItem("Sin filamento", None)
        filaments = self.inventory_manager.get_all_filaments()
        for filament in filaments:
            # filament es un diccionario
            display_text = f"{filament['brand']} - {filament['material_type']} ({filament['color']})"
            self.filament_combo.addItem(display_text, filament['id'])
    
    def save_project(self):
        """Guarda el proyecto."""
        name = self.name_input.text().strip()
        if not name:
            msg = QMessageBox(self)
            msg.setWindowTitle("Error")
            msg.setText("El nombre del proyecto es obligatorio")
            msg.setIcon(QMessageBox.Warning)
            msg.addButton("Aceptar", QMessageBox.AcceptRole)
            msg.exec_()
            return
        
        description = self.desc_input.toPlainText().strip()
        status = self.status_combo.currentText()
        model_id = self.model_combo.currentData()
        filament_id = self.filament_combo.currentData()
        weight = self.weight_input.value()
        time_hours = self.time_input.value()
        
        # Calcular costes si hay datos
        costs = {'filament_cost': 0, 'energy_cost': 0, 'total_cost': 0}
        if weight > 0 and time_hours > 0 and filament_id:
            # Obtener precio del filamento
            filament = self.inventory_manager.get_filament_by_id(filament_id)
            if filament:
                price_per_kg = filament[7]  # price
                costs = self.project_manager.calculate_costs(weight, price_per_kg, time_hours)
        
        if self.is_edit:
            # Actualizar proyecto existente
            success, message = self.project_manager.update_project(
                self.project[0],
                name=name,
                description=description,
                status=status,
                model_id=model_id,
                filament_id=filament_id,
                weight_grams=weight,
                print_time_hours=time_hours,
                **costs
            )
        else:
            # Crear nuevo proyecto
            success, message = self.project_manager.create_project(
                self.user_id, name, description, model_id, filament_id,
                weight, time_hours, status
            )
            
            # Actualizar costes
            if success:
                # Obtener el ID del proyecto recién creado y actualizar costes
                projects = self.project_manager.get_all_projects(self.user_id)
                if projects:
                    latest_project_id = projects[0][0]
                    self.project_manager.update_project(latest_project_id, **costs)
        
        if success:
            self.accept()
        else:
            msg = QMessageBox(self)
            msg.setWindowTitle("Error")
            msg.setText(message)
            msg.setIcon(QMessageBox.Warning)
            msg.addButton("Aceptar", QMessageBox.AcceptRole)
            msg.exec_()
    
    def get_input_style(self):
        return """
            QLineEdit, QTextEdit, QDoubleSpinBox {
                background-color: #3a3a3a;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 8px;
                color: white;
            }
        """
    
    def get_combo_style(self):
        return """
            QComboBox {
                background-color: #3a3a3a;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 8px;
                color: white;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #3a3a3a;
                color: white;
                selection-background-color: #007BFF;
            }
        """
