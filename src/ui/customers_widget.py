from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit,
    QGroupBox, QFormLayout, QMessageBox, QDialog, QDialogButtonBox,
    QTextEdit
)
from PyQt5.QtCore import Qt, pyqtSignal
from src.logic.customer_manager import CustomerManager
from src.ui.utils import MessageBoxHelper


class CustomersWidget(QWidget):
    data_changed = pyqtSignal()

    def __init__(self, user_id=None):
        super().__init__()
        self.user_id = user_id
        self.manager = CustomerManager()
        self.init_ui()
        self.load_table()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        title = QLabel("Clientes")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: white;")
        layout.addWidget(title)

        btn_add = QPushButton("+ Nuevo Cliente")
        btn_add.setObjectName("btn_success")
        btn_add.setCursor(Qt.PointingHandCursor)
        btn_add.clicked.connect(self.open_add_dialog)
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_row.addWidget(btn_add)
        layout.addLayout(btn_row)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Nombre", "Email", "Teléfono", "Dirección", "Acciones"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table)

        self.setLayout(layout)

    def load_table(self):
        self.table.setRowCount(0)
        customers = self.manager.get_all_customers(self.user_id)
        for r, c in enumerate(customers):
            self.table.insertRow(r)
            self.table.setItem(r, 0, QTableWidgetItem(str(c['id'])))
            self.table.setItem(r, 1, QTableWidgetItem(c['name']))
            self.table.setItem(r, 2, QTableWidgetItem(c.get('email') or ''))
            self.table.setItem(r, 3, QTableWidgetItem(c.get('phone') or ''))
            self.table.setItem(r, 4, QTableWidgetItem(c.get('address') or ''))

            btn_row = QWidget()
            btn_layout = QHBoxLayout(btn_row)
            btn_layout.setContentsMargins(4, 2, 4, 2)
            btn_layout.setSpacing(6)

            btn_edit = QPushButton("Editar")
            btn_edit.setObjectName("btn_primary_sm")
            btn_edit.setCursor(Qt.PointingHandCursor)
            btn_edit.clicked.connect(lambda checked, cid=c['id']: self.open_edit_dialog(cid))

            btn_del = QPushButton("Eliminar")
            btn_del.setObjectName("btn_danger_sm")
            btn_del.setCursor(Qt.PointingHandCursor)
            btn_del.clicked.connect(lambda checked, cid=c['id'], cname=c['name']: self.delete_customer(cid, cname))

            btn_layout.addWidget(btn_edit)
            btn_layout.addWidget(btn_del)
            btn_layout.addStretch()
            self.table.setCellWidget(r, 5, btn_row)
            self.table.setRowHeight(r, 40)

    def open_add_dialog(self):
        dialog = _CustomerDialog(self, self.user_id, manager=self.manager)
        if dialog.exec_() == QDialog.Accepted:
            self.load_table()
            self.data_changed.emit()

    def open_edit_dialog(self, customer_id):
        customer = self.manager.get_customer_by_id(customer_id)
        if customer:
            dialog = _CustomerDialog(self, self.user_id, manager=self.manager, customer=customer)
            if dialog.exec_() == QDialog.Accepted:
                self.load_table()
                self.data_changed.emit()

    def delete_customer(self, customer_id, name):
        if MessageBoxHelper.ask_confirmation(
            self.window(), "Confirmar eliminación",
            f"¿Eliminar el cliente '{name}'?\nSe cancelará si tiene pedidos asociados."
        ):
            ok, msg = self.manager.delete_customer(customer_id)
            if ok:
                self.load_table()
                self.data_changed.emit()
            else:
                MessageBoxHelper.show_warning(self.window(), "Error", msg)


class _CustomerDialog(QDialog):
    def __init__(self, parent, user_id, manager, customer=None):
        super().__init__(parent)
        self.user_id = user_id
        self.manager = manager
        self.customer = customer
        self.is_edit = customer is not None
        self.setWindowTitle("Editar Cliente" if self.is_edit else "Nuevo Cliente")
        self.setMinimumWidth(420)
        self.setObjectName("ProjectDialog")
        self.setStyleSheet("#ProjectDialog { background-color: #2C2C2C; color: white; }")
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        form = QFormLayout()
        form.setSpacing(10)

        self.name_input = QLineEdit()
        self.email_input = QLineEdit()
        self.phone_input = QLineEdit()
        self.address_input = QLineEdit()
        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(80)

        if self.is_edit:
            self.name_input.setText(self.customer.get('name', ''))
            self.email_input.setText(self.customer.get('email') or '')
            self.phone_input.setText(self.customer.get('phone') or '')
            self.address_input.setText(self.customer.get('address') or '')
            self.notes_input.setPlainText(self.customer.get('notes') or '')

        form.addRow("Nombre *:", self.name_input)
        form.addRow("Email:", self.email_input)
        form.addRow("Teléfono:", self.phone_input)
        form.addRow("Dirección:", self.address_input)
        form.addRow("Notas:", self.notes_input)
        layout.addLayout(form)

        btns = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        btns.accepted.connect(self._save)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

    def _save(self):
        name = self.name_input.text().strip()
        if not name:
            MessageBoxHelper.show_warning(self, "Error", "El nombre es obligatorio")
            return
        kwargs = dict(
            name=name,
            email=self.email_input.text().strip(),
            phone=self.phone_input.text().strip(),
            address=self.address_input.text().strip(),
            notes=self.notes_input.toPlainText().strip(),
        )
        if self.is_edit:
            ok, msg = self.manager.update_customer(self.customer['id'], **kwargs)
        else:
            ok, msg = self.manager.create_customer(self.user_id, **kwargs)
        if ok:
            self.accept()
        else:
            MessageBoxHelper.show_warning(self, "Error", msg)
