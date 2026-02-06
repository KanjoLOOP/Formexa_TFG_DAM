from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                             QTableWidgetItem, QPushButton, QHeaderView, QGroupBox, 
                             QFormLayout, QLineEdit, QComboBox, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal
from src.logic.inventory_manager import InventoryManager

class InventoryWidget(QWidget):
    data_changed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.manager = InventoryManager()
        self.init_ui()
        self.refresh_table()

    def init_ui(self):
        layout = QVBoxLayout()

        # --- Formulario de Añadir ---
        form_group = QGroupBox("Añadir Nuevo Filamento")
        form_layout = QHBoxLayout()

        self.input_brand = QLineEdit()
        self.input_brand.setPlaceholderText("Marca")
        form_layout.addWidget(self.input_brand)

        self.input_type = QComboBox()
        self.input_type.addItems(["PLA", "PETG", "ABS", "TPU", "ASA", "Otro"])
        self.input_type.setStyleSheet("""
            QComboBox {
                background-color: #333333;
                color: white;
                border: 1px solid #444;
                border-radius: 4px;
                padding: 5px;
            }
            QComboBox QAbstractItemView {
                background-color: #333333;
                color: white;
                selection-background-color: #555;
            }
        """)
        form_layout.addWidget(self.input_type)

        self.input_color = QComboBox()
        self.input_color.addItems([
            "Negro", "Blanco", "Gris", "Plateado", "Rojo", "Azul", 
            "Verde", "Amarillo", "Naranja", "Morado", "Rosa", 
            "Marrón", "Transparente", "Oro", "Cobre", "Bronce", "Otro"
        ])
        self.input_color.setStyleSheet("""
            QComboBox {
                background-color: #333333;
                color: white;
                border: 1px solid #444;
                border-radius: 4px;
                padding: 5px;
            }
            QComboBox QAbstractItemView {
                background-color: #333333;
                color: white;
                selection-background-color: #555;
            }
        """)
        form_layout.addWidget(self.input_color)

        self.input_weight = QLineEdit()
        self.input_weight.setPlaceholderText("Peso (g)")
        form_layout.addWidget(self.input_weight)

        self.input_price = QLineEdit()
        self.input_price.setPlaceholderText("Precio (€)")
        form_layout.addWidget(self.input_price)

        self.btn_add = QPushButton("Añadir")
        self.btn_add.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        self.btn_add.clicked.connect(self.add_filament)
        form_layout.addWidget(self.btn_add)

        form_group.setLayout(form_layout)
        layout.addWidget(form_group)

        # --- Tabla de Inventario ---
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Marca", "Tipo", "Color", "Peso Restante (g)", "Precio (€)"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False) # Ocultar barra lateral blanca (números de fila)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.table)

        # --- Botones de Acción ---
        action_layout = QHBoxLayout()
        self.btn_delete = QPushButton("Eliminar Seleccionado")
        self.btn_delete.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        self.btn_delete.clicked.connect(self.delete_filament)
        action_layout.addWidget(self.btn_delete)
        action_layout.addStretch()
        
        layout.addLayout(action_layout)

        self.setLayout(layout)

    def refresh_table(self):
        """Recarga la tabla con datos de la BD."""
        self.table.setRowCount(0)
        filaments = self.manager.get_all_filaments()
        
        if filaments:
            for row_idx, f in enumerate(filaments):
                self.table.insertRow(row_idx)
                self.table.setItem(row_idx, 0, QTableWidgetItem(str(f['id'])))
                self.table.setItem(row_idx, 1, QTableWidgetItem(f['brand']))
                self.table.setItem(row_idx, 2, QTableWidgetItem(f['material_type']))
                self.table.setItem(row_idx, 3, QTableWidgetItem(f['color']))
                self.table.setItem(row_idx, 4, QTableWidgetItem(str(f['weight_current'])))
                self.table.setItem(row_idx, 5, QTableWidgetItem(str(f['price'])))

    def add_filament(self):
        brand = self.input_brand.text()
        m_type = self.input_type.currentText()
        color = self.input_color.currentText()
        weight = self.input_weight.text()
        price = self.input_price.text()

        if not (brand and color and weight and price):
            QMessageBox.warning(self, "Error", "Todos los campos son obligatorios.")
            return

        try:
            weight_val = float(weight)
            price_val = float(price)
            
            success, msg = self.manager.add_filament(brand, m_type, color, weight_val, price_val)
            if success:
                self.refresh_table()
                self.clear_inputs()
                
                msg_box = QMessageBox(self)
                msg_box.setWindowTitle("Éxito")
                msg_box.setText(msg)
                msg_box.setIcon(QMessageBox.Information)
                msg_box.addButton("Aceptar", QMessageBox.AcceptRole)
                msg_box.exec_()
                self.data_changed.emit() # Emitir señal de cambio
            else:
                msg_box = QMessageBox(self)
                msg_box.setWindowTitle("Error")
                msg_box.setText(msg)
                msg_box.setIcon(QMessageBox.Warning)
                msg_box.addButton("Aceptar", QMessageBox.AcceptRole)
                msg_box.exec_()
        except ValueError:
            msg = QMessageBox(self)
            msg.setWindowTitle("Error")
            msg.setText("Peso y Precio deben ser numéricos.")
            msg.setIcon(QMessageBox.Warning)
            msg.addButton("Aceptar", QMessageBox.AcceptRole)
            msg.exec_()

    def delete_filament(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            return

        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Confirmar")
        msg_box.setText("¿Eliminar filamento seleccionado?")
        msg_box.setIcon(QMessageBox.Question)
        btn_si = msg_box.addButton("Sí", QMessageBox.YesRole)
        btn_no = msg_box.addButton("No", QMessageBox.NoRole)
        msg_box.exec_()
        
        if msg_box.clickedButton() == btn_si:
            row = selected_rows[0].row()
            f_id = int(self.table.item(row, 0).text())
            
            if self.manager.delete_filament(f_id):
                self.refresh_table()
                self.data_changed.emit() # Emitir señal de cambio
            else:
                msg_box = QMessageBox(self)
                msg_box.setWindowTitle("Error")
                msg_box.setText("No se pudo eliminar.")
                msg_box.setIcon(QMessageBox.Warning)
                msg_box.addButton("Aceptar", QMessageBox.AcceptRole)
                msg_box.exec_()

    def clear_inputs(self):
        self.input_brand.clear()
        self.input_color.setCurrentIndex(0)
        self.input_weight.clear()
        self.input_price.clear()
