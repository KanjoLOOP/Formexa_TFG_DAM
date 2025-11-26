from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QListWidget, QFileDialog, QMessageBox, QSplitter)
from PyQt5.QtCore import Qt
from src.logic.library_manager import LibraryManager
from src.ui.viewer_3d import Viewer3DWidget

class LibraryWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.manager = LibraryManager()
        self.init_ui()
        self.refresh_list()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # Toolbar superior con botones
        toolbar = QHBoxLayout()
        self.btn_add = QPushButton("+ Añadir Modelo")
        self.btn_add.clicked.connect(self.add_model)
        self.btn_delete = QPushButton("Eliminar")
        self.btn_delete.setStyleSheet("background-color: #8b0000; color: white;")
        self.btn_delete.clicked.connect(self.delete_model)
        
        toolbar.addWidget(self.btn_add)
        toolbar.addWidget(self.btn_delete)
        toolbar.addStretch()
        
        layout.addLayout(toolbar)
        
        # Splitter para redimensionar
        splitter = QSplitter(Qt.Horizontal)

        # Panel Izquierdo: Solo Lista
        self.model_list = QListWidget()
        self.model_list.itemClicked.connect(self.on_model_selected)
        
        splitter.addWidget(self.model_list)

        # Panel Derecho: Visor 3D
        self.viewer = Viewer3DWidget()
        splitter.addWidget(self.viewer)
        
        # Configuración inicial del splitter - Fijo para mantener proporción
        splitter.setSizes([300, 700])
        splitter.setStretchFactor(0, 0)  # Panel izquierdo no se estira
        splitter.setStretchFactor(1, 1)  # Panel derecho se estira
        self.model_list.setMinimumWidth(250)
        self.model_list.setMaximumWidth(350)

        layout.addWidget(splitter)
        self.setLayout(layout)

    def refresh_list(self):
        """Recarga la lista de modelos desde la BD."""
        self.model_list.clear()
        models = self.manager.get_all_models()
        if models:
            for model in models:
                self.model_list.addItem(model['name'])
                # Guardamos el ID en el item para referencia
                item = self.model_list.item(self.model_list.count() - 1)
                item.setData(Qt.UserRole, model['id'])
                item.setData(Qt.UserRole + 1, model['file_path'])

    def add_model(self):
        """Abre diálogo para seleccionar archivo STL."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Seleccionar Modelo 3D", "", "Archivos STL (*.stl)")
        if file_path:
            # Pedir nombre (opcional, por ahora usamos nombre de archivo)
            import os
            name = os.path.basename(file_path)
            
            success, msg = self.manager.add_model(file_path, name)
            if success:
                self.refresh_list()
                QMessageBox.information(self, "Éxito", msg)
            else:
                QMessageBox.warning(self, "Error", msg)

    def delete_model(self):
        """Elimina el modelo seleccionado."""
        current_item = self.model_list.currentItem()
        if not current_item:
            return
        
        model_id = current_item.data(Qt.UserRole)
        confirm = QMessageBox.question(self, "Confirmar", "¿Estás seguro de eliminar este modelo?", 
                                       QMessageBox.Yes | QMessageBox.No)
        
        if confirm == QMessageBox.Yes:
            if self.manager.delete_model(model_id):
                self.refresh_list()
                self.viewer.ax.clear() # Limpiar visor
                self.viewer.canvas.draw()
            else:
                QMessageBox.warning(self, "Error", "No se pudo eliminar el modelo.")

    def on_model_selected(self, item):
        """Carga el modelo en el visor cuando se selecciona."""
        file_path = item.data(Qt.UserRole + 1)
        self.viewer.load_model(file_path)
