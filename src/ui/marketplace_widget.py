from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, 
                             QPushButton, QScrollArea, QFrame, QMessageBox, QGraphicsDropShadowEffect, QSizePolicy,
                             QDialog, QFormLayout, QLineEdit, QDialogButtonBox, QFileDialog)
from PyQt5.QtGui import QPixmap, QColor
from PyQt5.QtCore import Qt
import os

class MarketplaceWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # Fondo general oscuro
        self.setStyleSheet("background-color: #1E1E1E;")

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Encabezado oscuro
        header = QFrame()
        header.setStyleSheet("background-color: #222222; padding: 20px;")
        header_layout = QHBoxLayout(header) # Changed to HBox for button
        
        title = QLabel("Marketplace de Modelos 3D")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: white; letter-spacing: 1px;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        btn_upload = QPushButton("Subir Modelo")
        btn_upload.setCursor(Qt.PointingHandCursor)
        btn_upload.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        btn_upload.clicked.connect(self.open_upload_dialog)
        header_layout.addWidget(btn_upload)
        
        layout.addWidget(header)

        # Área de scroll principal
        main_scroll = QScrollArea()
        main_scroll.setWidgetResizable(True)
        main_scroll.setStyleSheet("border: none; background-color: #1E1E1E;")
        
        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: #1E1E1E;")
        self.main_layout = QVBoxLayout(content_widget)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(30)

        # Datos simulados
        self.mock_items = [
            {"name": "Soporte Auriculares", "price": "Gratis", "desc": "Soporte universal para mesa.", "category": "recommended"},
            {"name": "Maceta Low Poly", "price": "2.50 €", "desc": "Diseño geométrico moderno.", "category": "top"},
            {"name": "Engranaje Helicoidal", "price": "5.00 €", "desc": "Pieza mecánica funcional.", "category": "all"},
            {"name": "Figura Dragón", "price": "10.00 €", "desc": "Modelo detallado para resina.", "category": "top"},
            {"name": "Caja Organizadora", "price": "Gratis", "desc": "Modular y apilable.", "category": "recommended"},
            {"name": "Llavero Personalizable", "price": "1.00 €", "desc": "Fácil de editar.", "category": "all"},
            {"name": "Soporte Móvil", "price": "Gratis", "desc": "Ajustable y plegable.", "category": "recommended"},
            {"name": "Vaso Geométrico", "price": "3.00 €", "desc": "Estilo voronoi.", "category": "top"},
            {"name": "Clip Cables", "price": "0.50 €", "desc": "Organizador de escritorio.", "category": "all"},
            {"name": "Estatua Moai", "price": "Gratis", "desc": "Réplica histórica.", "category": "all"},
            {"name": "Carcasa Raspberry Pi", "price": "4.00 €", "desc": "Ventilación optimizada.", "category": "recommended"},
            {"name": "Juguete Articulado", "price": "6.00 €", "desc": "Dragón flexible.", "category": "top"},
            {"name": "Lámpara Litofanía", "price": "8.00 €", "desc": "Personalizable con fotos.", "category": "all"},
            {"name": "Organizador Herramientas", "price": "Gratis", "desc": "Para taller.", "category": "all"}
        ]

        # Categorías
        recommended_items = [i for i in self.mock_items if i.get('category') == 'recommended']
        top_items = [i for i in self.mock_items if i.get('category') == 'top']
        self.all_items = self.mock_items # Todos los items (guardar en self para resize)

        # Sección: Recomendados para ti
        self.create_horizontal_section("Recomendados para ti", recommended_items)

        # Sección: Los más comprados
        self.create_horizontal_section("Los más comprados", top_items)

        # Sección: Todos los modelos (Grid dinámico)
        self.create_grid_section("Todos los modelos")

        # Spacer final
        self.main_layout.addStretch()

        main_scroll.setWidget(content_widget)
        layout.addWidget(main_scroll)
        self.setLayout(layout)

    def resizeEvent(self, event):
        """Recalcular columnas del grid al redimensionar."""
        self.update_grid_columns()
        super().resizeEvent(event)

    def create_horizontal_section(self, title_text, items):
        # Contenedor de la sección
        section_widget = QWidget()
        section_layout = QVBoxLayout(section_widget)
        section_layout.setContentsMargins(0, 0, 0, 0)
        section_layout.setSpacing(10)

        # Título
        title = QLabel(title_text)
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #e0e0e0; margin-left: 5px;")
        section_layout.addWidget(title)

        # Scroll Horizontal
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFixedHeight(370) # Altura fija para la fila
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("border: none; background-color: transparent;")

        scroll_content = QWidget()
        scroll_content.setStyleSheet("background-color: transparent;")
        scroll_layout = QHBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(5, 5, 5, 5)
        scroll_layout.setSpacing(15)
        scroll_layout.setAlignment(Qt.AlignLeft)

        for item in items:
            card = self.create_item_card(item)
            scroll_layout.addWidget(card)

        scroll.setWidget(scroll_content)
        section_layout.addWidget(scroll)
        
        self.main_layout.addWidget(section_widget)

    def create_grid_section(self, title_text):
        # Contenedor de la sección
        section_widget = QWidget()
        section_layout = QVBoxLayout(section_widget)
        section_layout.setContentsMargins(0, 0, 0, 0)
        section_layout.setSpacing(15)

        # Título
        title = QLabel(title_text)
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #e0e0e0; margin-left: 5px; margin-top: 10px;")
        section_layout.addWidget(title)

        # Grid Layout Widget
        grid_widget = QWidget()
        self.items_grid_layout = QGridLayout(grid_widget)
        self.items_grid_layout.setContentsMargins(5, 5, 5, 5)
        self.items_grid_layout.setSpacing(20)

        section_layout.addWidget(grid_widget)
        self.main_layout.addWidget(section_widget)

    def update_grid_columns(self):
        """Actualiza el número de columnas basado en el ancho disponible."""
        if not hasattr(self, 'items_grid_layout') or not self.all_items:
            return

        # Limpiar grid actual
        for i in reversed(range(self.items_grid_layout.count())): 
            self.items_grid_layout.itemAt(i).widget().setParent(None)

        # Calcular columnas
        available_width = self.width() - 60 # Margen aprox
        card_width = 260 + 20 # Ancho tarjeta + spacing
        num_columns = max(1, available_width // card_width)

        # Repoblar grid
        for i, item in enumerate(self.all_items):
            card = self.create_item_card(item)
            row = i // num_columns
            col = i % num_columns
            self.items_grid_layout.addWidget(card, row, col)

    def create_item_card(self, item_data):
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #2C2C2C;
                border-radius: 12px;
                border: 1px solid #3a3a3a;
            }
            QFrame:hover {
                border: 1px solid #007BFF;
                background-color: #333333;
            }
        """)
        card.setFixedSize(260, 340)
        
        # Sombra sutil
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 4)
        card.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # Imagen (Placeholder o Real)
        img_label = QLabel()
        img_label.setAlignment(Qt.AlignCenter)
        img_label.setStyleSheet("background-color: #222; border-radius: 8px;")
        img_label.setFixedHeight(160)
        
        # Intentar cargar imagen del item si existe
        image_path = item_data.get("image")
        pixmap = None
        
        if image_path and os.path.exists(image_path):
            pixmap = QPixmap(image_path)
        else:
            # Fallback a placeholder por defecto
            pixmap = QPixmap("assets/model_placeholder.png")
            
        if pixmap and not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(230, 160, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            img_label.setPixmap(scaled_pixmap)
        else:
            img_label.setText("IMG")
            img_label.setStyleSheet("background-color: #222; color: #666; font-weight: bold; font-size: 20px; border-radius: 8px;")
            
        layout.addWidget(img_label)

        # Info
        name = QLabel(item_data["name"])
        name.setStyleSheet("font-size: 16px; font-weight: bold; color: white; border: none; background: transparent;")
        layout.addWidget(name)

        desc = QLabel(item_data["desc"])
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #B0B0B0; font-size: 13px; border: none; background: transparent;")
        layout.addWidget(desc)

        price = QLabel(item_data["price"])
        price.setStyleSheet("color: #007BFF; font-weight: bold; font-size: 15px; border: none; background: transparent;")
        layout.addWidget(price)

        btn_buy = QPushButton("Obtener" if item_data["price"] == "Gratis" else "Comprar")
        btn_buy.setCursor(Qt.PointingHandCursor)
        btn_buy.setStyleSheet("""
            QPushButton {
                background-color: #007BFF;
                color: white;
                border-radius: 6px;
                padding: 8px;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover {
                background-color: #1a8cff;
            }
            QPushButton:pressed {
                background-color: #0056b3;
            }
        """)
        btn_buy.clicked.connect(lambda: self.buy_item(item_data["name"]))
        layout.addWidget(btn_buy)

        return card

    def open_upload_dialog(self):
        """Abre un diálogo para subir un modelo."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Subir Modelo al Marketplace")
        dialog.setFixedSize(450, 400)
        dialog.setStyleSheet("background-color: #2C2C2C; color: white;")
        
        layout = QVBoxLayout(dialog)
        
        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        
        name_input = QLineEdit()
        name_input.setStyleSheet("background-color: #3a3a3a; border: 1px solid #555; padding: 5px; color: white;")
        form_layout.addRow("Nombre del Modelo:", name_input)
        
        price_input = QLineEdit()
        price_input.setPlaceholderText("Ej: 5.00 € o Gratis")
        price_input.setStyleSheet("background-color: #3a3a3a; border: 1px solid #555; padding: 5px; color: white;")
        form_layout.addRow("Precio:", price_input)
        
        desc_input = QLineEdit()
        desc_input.setPlaceholderText("Breve descripción")
        desc_input.setStyleSheet("background-color: #3a3a3a; border: 1px solid #555; padding: 5px; color: white;")
        form_layout.addRow("Descripción:", desc_input)
        
        # Selector de Imagen
        img_layout = QHBoxLayout()
        img_input = QLineEdit()
        img_input.setReadOnly(True)
        img_input.setPlaceholderText("Seleccionar imagen...")
        img_input.setStyleSheet("background-color: #3a3a3a; border: 1px solid #555; padding: 5px; color: #aaa;")
        btn_img = QPushButton("Examinar")
        btn_img.setStyleSheet("background-color: #555; color: white; border-radius: 4px; padding: 5px;")
        
        def select_image():
            path, _ = QFileDialog.getOpenFileName(dialog, "Seleccionar Imagen", "", "Imágenes (*.png *.jpg *.jpeg)")
            if path:
                img_input.setText(path)
        
        btn_img.clicked.connect(select_image)
        img_layout.addWidget(img_input)
        img_layout.addWidget(btn_img)
        form_layout.addRow("Imagen:", img_layout)

        # Selector de STL
        stl_layout = QHBoxLayout()
        stl_input = QLineEdit()
        stl_input.setReadOnly(True)
        stl_input.setPlaceholderText("Seleccionar archivo STL...")
        stl_input.setStyleSheet("background-color: #3a3a3a; border: 1px solid #555; padding: 5px; color: #aaa;")
        btn_stl = QPushButton("Examinar")
        btn_stl.setStyleSheet("background-color: #555; color: white; border-radius: 4px; padding: 5px;")
        
        def select_stl():
            path, _ = QFileDialog.getOpenFileName(dialog, "Seleccionar STL", "", "Archivos STL (*.stl)")
            if path:
                stl_input.setText(path)
        
        btn_stl.clicked.connect(select_stl)
        stl_layout.addWidget(stl_input)
        stl_layout.addWidget(btn_stl)
        form_layout.addRow("Archivo STL:", stl_layout)
        
        layout.addLayout(form_layout)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        buttons.setStyleSheet("QPushButton { background-color: #007BFF; color: white; padding: 6px 12px; border-radius: 4px; }")
        layout.addWidget(buttons)
        
        if dialog.exec_() == QDialog.Accepted:
            name = name_input.text()
            price = price_input.text()
            desc = desc_input.text()
            img_path = img_input.text()
            stl_path = stl_input.text()
            
            if name and price:
                self.upload_model(name, price, desc, img_path, stl_path)
            else:
                QMessageBox.warning(self, "Error", "El nombre y el precio son obligatorios.")

    def upload_model(self, name, price, desc, img_path, stl_path):
        """Simula la subida de un modelo."""
        new_item = {
            "name": name,
            "price": price,
            "desc": desc if desc else "Sin descripción",
            "category": "all", # Por defecto a 'Todos'
            "image": img_path if img_path else None,
            "stl_path": stl_path if stl_path else None
        }
        
        self.mock_items.append(new_item)
        self.all_items = self.mock_items
        
        # Simplemente repoblar el grid de 'Todos los modelos'
        self.update_grid_columns()
        
        QMessageBox.information(self, "Éxito", f"Modelo '{name}' subido correctamente al Marketplace.")

    def buy_item(self, name):
        # Simulación de compra
        QMessageBox.information(self, "Compra Exitosa", f"Has adquirido '{name}'.\n(Simulación: El modelo se añadiría a tu biblioteca)")
