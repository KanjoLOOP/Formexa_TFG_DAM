from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit,
    QComboBox, QDoubleSpinBox, QSpinBox, QDialog, QDialogButtonBox,
    QFormLayout, QFileDialog, QDateEdit
)
from PyQt5.QtCore import Qt, QDate
from src.logic.order_manager import OrderManager
from src.logic.customer_manager import CustomerManager
from src.logic.project_manager import ProjectManager
from src.logic.report_generator import ReportGenerator
from src.ui.utils import MessageBoxHelper


class OrdersWidget(QWidget):
    def __init__(self, user_id=None):
        super().__init__()
        self.user_id = user_id
        self.order_mgr = OrderManager()
        self.customer_mgr = CustomerManager()
        self.project_mgr = ProjectManager()
        self.report_gen = ReportGenerator()
        self.init_ui()
        self.load_table()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        title = QLabel("Pedidos")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: white;")
        layout.addWidget(title)

        # Stats row
        self.stats_label = QLabel()
        self.stats_label.setStyleSheet("color: #aaa; font-size: 13px;")
        layout.addWidget(self.stats_label)

        btn_add = QPushButton("+ Nuevo Pedido")
        btn_add.setObjectName("btn_success")
        btn_add.setCursor(Qt.PointingHandCursor)
        btn_add.clicked.connect(self.open_add_dialog)
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_row.addWidget(btn_add)
        layout.addLayout(btn_row)

        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "ID", "Cliente", "Proyecto", "Estado", "Cant.", "P. Unit.", "Total", "Acciones"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table)

        self.setLayout(layout)

    def load_table(self):
        self.table.setRowCount(0)
        orders = self.order_mgr.get_all_orders(self.user_id)

        for r, o in enumerate(orders):
            self.table.insertRow(r)
            self.table.setItem(r, 0, QTableWidgetItem(str(o['id'])))
            self.table.setItem(r, 1, QTableWidgetItem(o.get('customer_name') or '-'))
            self.table.setItem(r, 2, QTableWidgetItem(o.get('project_name') or '-'))
            self.table.setItem(r, 3, QTableWidgetItem(o.get('status') or '-'))
            self.table.setItem(r, 4, QTableWidgetItem(str(o.get('quantity', 1))))
            self.table.setItem(r, 5, QTableWidgetItem(f"{o.get('unit_price', 0):.2f} €"))
            self.table.setItem(r, 6, QTableWidgetItem(f"{o.get('total_price', 0):.2f} €"))

            btn_row = QWidget()
            btn_layout = QHBoxLayout(btn_row)
            btn_layout.setContentsMargins(4, 2, 4, 2)
            btn_layout.setSpacing(4)

            btn_edit = QPushButton("Editar")
            btn_edit.setObjectName("btn_primary_sm")
            btn_edit.setCursor(Qt.PointingHandCursor)
            btn_edit.clicked.connect(lambda checked, oid=o['id']: self.open_edit_dialog(oid))

            btn_pdf = QPushButton("PDF")
            btn_pdf.setObjectName("btn_success_sm")
            btn_pdf.setCursor(Qt.PointingHandCursor)
            btn_pdf.clicked.connect(lambda checked, oid=o['id']: self.export_pdf(oid))

            btn_del = QPushButton("Eliminar")
            btn_del.setObjectName("btn_danger_sm")
            btn_del.setCursor(Qt.PointingHandCursor)
            btn_del.clicked.connect(lambda checked, oid=o['id']: self.delete_order(oid))

            btn_layout.addWidget(btn_edit)
            btn_layout.addWidget(btn_pdf)
            btn_layout.addWidget(btn_del)
            btn_layout.addStretch()
            self.table.setCellWidget(r, 7, btn_row)
            self.table.setRowHeight(r, 40)

        # Update stats
        stats = self.order_mgr.get_revenue_stats(self.user_id)
        if stats:
            rev = stats.get('revenue') or 0
            pend = stats.get('pending_revenue') or 0
            total = stats.get('total_orders') or 0
            self.stats_label.setText(
                f"Total pedidos: {total}  |  Ingresos cobrados: {rev:.2f} €  |  Pendiente de cobro: {pend:.2f} €"
            )

    def open_add_dialog(self):
        customers = self.customer_mgr.get_all_customers(self.user_id)
        if not customers:
            MessageBoxHelper.show_warning(self, "Sin clientes",
                                          "Crea al menos un cliente antes de crear un pedido.")
            return
        projects = self.project_mgr.get_all_projects(self.user_id)
        dialog = _OrderDialog(self, self.user_id, self.order_mgr, customers, projects)
        if dialog.exec_() == QDialog.Accepted:
            self.load_table()

    def open_edit_dialog(self, order_id):
        order = self.order_mgr.get_order_by_id(order_id)
        if not order:
            return
        customers = self.customer_mgr.get_all_customers(self.user_id)
        projects = self.project_mgr.get_all_projects(self.user_id)
        dialog = _OrderDialog(self, self.user_id, self.order_mgr, customers, projects, order=order)
        if dialog.exec_() == QDialog.Accepted:
            self.load_table()

    def export_pdf(self, order_id):
        order = self.order_mgr.get_order_by_id(order_id)
        if not order:
            return
        customer = self.customer_mgr.get_customer_by_id(order['customer_id'])
        project = None
        if order.get('project_id'):
            project = self.project_mgr.get_project_by_id(order['project_id'])

        path, _ = QFileDialog.getSaveFileName(
            self, "Guardar PDF", f"pedido_{order_id}.pdf", "PDF (*.pdf)"
        )
        if not path:
            return
        if not path.endswith('.pdf'):
            path += '.pdf'
        try:
            self.report_gen.generate_quote_pdf(order, customer, project, path)
            MessageBoxHelper.show_info(self, "Éxito", "PDF generado correctamente.")
        except Exception as e:
            MessageBoxHelper.show_warning(self, "Error", f"No se pudo generar el PDF: {e}")

    def delete_order(self, order_id):
        if MessageBoxHelper.ask_confirmation(self.window(), "Confirmar", "¿Eliminar este pedido?"):
            ok, msg = self.order_mgr.delete_order(order_id)
            if ok:
                self.load_table()
            else:
                MessageBoxHelper.show_warning(self.window(), "Error", msg)


class _OrderDialog(QDialog):
    def __init__(self, parent, user_id, order_mgr, customers, projects, order=None):
        super().__init__(parent)
        self.user_id = user_id
        self.order_mgr = order_mgr
        self.customers = customers
        self.projects = projects
        self.order = order
        self.is_edit = order is not None
        self.setWindowTitle("Editar Pedido" if self.is_edit else "Nuevo Pedido")
        self.setMinimumWidth(460)
        self.setObjectName("ProjectDialog")
        self.setStyleSheet("#ProjectDialog { background-color: #2C2C2C; color: white; }")
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        form = QFormLayout()
        form.setSpacing(10)

        self.customer_combo = QComboBox()
        for c in self.customers:
            self.customer_combo.addItem(c['name'], c['id'])

        self.project_combo = QComboBox()
        self.project_combo.addItem("Sin proyecto vinculado", None)
        for p in self.projects:
            self.project_combo.addItem(p['name'], p['id'])

        self.status_combo = QComboBox()
        self.status_combo.addItems(OrderManager.STATUSES)

        self.qty_spin = QSpinBox()
        self.qty_spin.setRange(1, 9999)
        self.qty_spin.valueChanged.connect(self._update_total)

        self.unit_price_spin = QDoubleSpinBox()
        self.unit_price_spin.setRange(0, 99999)
        self.unit_price_spin.setDecimals(2)
        self.unit_price_spin.setSuffix(" €")
        self.unit_price_spin.valueChanged.connect(self._update_total)

        self.total_label = QLabel("0.00 €")
        self.total_label.setStyleSheet("font-weight: bold; color: #28a745;")

        self.delivery_date = QDateEdit()
        self.delivery_date.setCalendarPopup(True)
        self.delivery_date.setDate(QDate.currentDate())
        self.delivery_date.setSpecialValueText("Sin fecha")

        if self.is_edit:
            o = self.order
            idx = self.customer_combo.findData(o['customer_id'])
            if idx >= 0:
                self.customer_combo.setCurrentIndex(idx)
            idx = self.project_combo.findData(o.get('project_id'))
            if idx >= 0:
                self.project_combo.setCurrentIndex(idx)
            idx = self.status_combo.findText(o.get('status', ''))
            if idx >= 0:
                self.status_combo.setCurrentIndex(idx)
            self.qty_spin.setValue(o.get('quantity', 1))
            self.unit_price_spin.setValue(o.get('unit_price', 0))
            if o.get('delivery_date'):
                try:
                    d = QDate.fromString(str(o['delivery_date']), "yyyy-MM-dd")
                    if d.isValid():
                        self.delivery_date.setDate(d)
                except Exception:
                    pass

        self._update_total()

        form.addRow("Cliente *:", self.customer_combo)
        form.addRow("Proyecto:", self.project_combo)
        form.addRow("Estado:", self.status_combo)
        form.addRow("Cantidad:", self.qty_spin)
        form.addRow("Precio unitario:", self.unit_price_spin)
        form.addRow("Total:", self.total_label)
        form.addRow("Entrega:", self.delivery_date)
        layout.addLayout(form)

        btns = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        btns.accepted.connect(self._save)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

    def _update_total(self):
        total = self.qty_spin.value() * self.unit_price_spin.value()
        self.total_label.setText(f"{total:.2f} €")

    def _save(self):
        customer_id = self.customer_combo.currentData()
        project_id = self.project_combo.currentData()
        status = self.status_combo.currentText()
        quantity = self.qty_spin.value()
        unit_price = self.unit_price_spin.value()
        delivery_date = self.delivery_date.date().toString("yyyy-MM-dd")

        if self.is_edit:
            total_price = round(unit_price * quantity, 2)
            ok, msg = self.order_mgr.update_order(
                self.order['id'],
                customer_id=customer_id, project_id=project_id, status=status,
                quantity=quantity, unit_price=unit_price, total_price=total_price,
                delivery_date=delivery_date
            )
        else:
            ok, msg = self.order_mgr.create_order(
                self.user_id, customer_id, unit_price, quantity=quantity,
                project_id=project_id, delivery_date=delivery_date
            )
            if ok and status != 'Presupuesto':
                last_orders = self.order_mgr.get_all_orders(self.user_id)
                if last_orders:
                    self.order_mgr.update_order(last_orders[0]['id'], status=status)

        if ok:
            self.accept()
        else:
            from src.ui.utils import MessageBoxHelper
            MessageBoxHelper.show_warning(self, "Error", msg)
