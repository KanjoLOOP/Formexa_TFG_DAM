from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QFormLayout, QGroupBox, QSpinBox)
from PyQt5.QtCore import Qt
from src.logic.cost_calculator import CostCalculator

class CalculatorWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.calculator = CostCalculator()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Título
        title = QLabel("Calculadora de Costes y Precio de Venta")
        title.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 10px; color: #e0e0e0;")
        layout.addWidget(title)

        # === PARÁMETROS DE CÁLCULO (ARRIBA) ===
        params_group = QGroupBox("Parámetros de Cálculo")
        params_layout = QFormLayout()

        self.input_price_kg = QLineEdit()
        self.input_price_kg.setPlaceholderText("Ej: 20.00")
        self.input_price_kg.setText("20")
        params_layout.addRow("Precio del Filamento (€/kg):", self.input_price_kg)

        self.input_power = QLineEdit()
        self.input_power.setText("350")
        params_layout.addRow("Consumo Impresora (Watts):", self.input_power)

        self.input_energy_cost = QLineEdit()
        self.input_energy_cost.setText("0.15")
        params_layout.addRow("Coste Energía (€/kWh):", self.input_energy_cost)

        params_group.setLayout(params_layout)
        layout.addWidget(params_group)

        # === SECCIÓN PIEZA ===
        pieza_group = QGroupBox("Pieza")
        pieza_group.setStyleSheet("QGroupBox { font-weight: bold; color: #b0b0b0; }")
        pieza_layout = QFormLayout()

        # Tiempo de impresión (Horas y Minutos)
        time_layout = QHBoxLayout()
        self.input_hours = QSpinBox()
        self.input_hours.setRange(0, 999)
        self.input_hours.setSuffix(" h")
        self.input_hours.setValue(5)
        
        self.input_minutes = QSpinBox()
        self.input_minutes.setRange(0, 59)
        self.input_minutes.setSuffix(" min")
        self.input_minutes.setValue(0)
        
        time_layout.addWidget(QLabel("Horas:"))
        time_layout.addWidget(self.input_hours)
        time_layout.addWidget(QLabel("Minutos:"))
        time_layout.addWidget(self.input_minutes)
        time_layout.addStretch()
        
        pieza_layout.addRow("Tiempo de impresión:", time_layout)

        # Gramos de filamento
        self.input_weight = QLineEdit()
        self.input_weight.setPlaceholderText("Ej: 157")
        pieza_layout.addRow("Gramos de filamento:", self.input_weight)

        # Insumos (EUR €)
        self.input_supplies = QLineEdit()
        self.input_supplies.setPlaceholderText("Ej: 0")
        self.input_supplies.setText("0")
        pieza_layout.addRow("INSUMOS (EUR €):", self.input_supplies)

        pieza_group.setLayout(pieza_layout)
        layout.addWidget(pieza_group)

        # === SECCIÓN GANANCIA ===
        ganancia_group = QGroupBox("Ganancia")
        ganancia_group.setStyleSheet("QGroupBox { font-weight: bold; color: #b0b0b0; }")
        ganancia_layout = QVBoxLayout()

        # Margen de ganancia (multiplicador)
        margin_layout = QFormLayout()
        self.input_margin = QLineEdit()
        self.input_margin.setPlaceholderText("Ej: 4")
        self.input_margin.setText("4")
        margin_layout.addRow("Margen de ganancia (multiplicador):", self.input_margin)
        ganancia_layout.addLayout(margin_layout)

        # Referencias
        ref_label = QLabel("Referencias:")
        ref_label.setStyleSheet("color: #8b0000; font-weight: bold; margin-top: 10px;")
        ganancia_layout.addWidget(ref_label)

        ref_text = QLabel("Precio Minorista → 4\nPrecio Mayorista → 3\nPrecio Llaveros → 5")
        ref_text.setStyleSheet("color: #b0b0b0; margin-left: 10px; font-size: 12px;")
        ganancia_layout.addWidget(ref_text)

        ganancia_group.setLayout(ganancia_layout)
        layout.addWidget(ganancia_group)

        # Botón Calcular
        self.btn_calculate = QPushButton("Calcular Precio de Venta")
        self.btn_calculate.clicked.connect(self.calculate)
        self.btn_calculate.setStyleSheet("font-size: 14px; padding: 10px; font-weight: bold;")
        layout.addWidget(self.btn_calculate)

        # === RESULTADOS (AL FINAL) ===
        results_group = QGroupBox("Resultados")
        results_layout = QVBoxLayout()

        self.lbl_filament_cost = QLabel("Coste Filamento: 0.00 €")
        self.lbl_filament_cost.setStyleSheet("color: #e0e0e0;")
        
        self.lbl_energy_cost = QLabel("Coste Energía: 0.00 €")
        self.lbl_energy_cost.setStyleSheet("color: #e0e0e0;")
        
        self.lbl_supplies_cost = QLabel("Coste Insumos: 0.00 €")
        self.lbl_supplies_cost.setStyleSheet("color: #e0e0e0;")
        
        self.lbl_total_cost = QLabel("COSTE TOTAL: 0.00 €")
        self.lbl_total_cost.setStyleSheet("font-size: 16px; font-weight: bold; color: #b0b0b0;")
        
        self.lbl_sale_price = QLabel("PRECIO DE VENTA: 0.00 €")
        self.lbl_sale_price.setStyleSheet("font-size: 18px; font-weight: bold; color: #e0e0e0; margin-top: 10px;")

        results_layout.addWidget(self.lbl_filament_cost)
        results_layout.addWidget(self.lbl_energy_cost)
        results_layout.addWidget(self.lbl_supplies_cost)
        results_layout.addWidget(self.lbl_total_cost)
        results_layout.addWidget(self.lbl_sale_price)
        
        results_group.setLayout(results_layout)
        layout.addWidget(results_group)

        layout.addStretch()
        self.setLayout(layout)

    def calculate(self):
        try:
            # Obtener valores
            hours = self.input_hours.value()
            minutes = self.input_minutes.value()
            total_time = hours + (minutes / 60.0)  # Convertir a horas decimales
            
            weight = float(self.input_weight.text() or 0)
            supplies = float(self.input_supplies.text() or 0)
            margin = float(self.input_margin.text() or 1)
            
            price_kg = float(self.input_price_kg.text() or 0)
            power = float(self.input_power.text() or 0)
            energy_price = float(self.input_energy_cost.text() or 0)

            # Calcular costes
            filament_cost = self.calculator.calculate_filament_cost(weight, price_kg)
            energy_cost = self.calculator.calculate_energy_cost(power, total_time, energy_price)
            total_cost = self.calculator.calculate_total_cost(filament_cost, energy_cost, supplies)
            
            # Calcular precio de venta
            sale_price = self.calculator.calculate_sale_price(total_cost, margin)

            # Mostrar resultados con colores discretos
            self.lbl_filament_cost.setText(f"Coste Filamento: {filament_cost:.2f} €")
            self.lbl_energy_cost.setText(f"Coste Energía: {energy_cost:.2f} €")
            self.lbl_supplies_cost.setText(f"Coste Insumos: {supplies:.2f} €")
            self.lbl_total_cost.setText(f"COSTE TOTAL: {total_cost:.2f} €")
            self.lbl_sale_price.setText(f"PRECIO DE VENTA: {sale_price:.2f} €")
            
            # Restaurar estilos
            self.lbl_filament_cost.setStyleSheet("color: #e0e0e0;")
            self.lbl_energy_cost.setStyleSheet("color: #e0e0e0;")
            self.lbl_supplies_cost.setStyleSheet("color: #e0e0e0;")
            self.lbl_total_cost.setStyleSheet("font-size: 16px; font-weight: bold; color: #b0b0b0;")
            self.lbl_sale_price.setStyleSheet("font-size: 18px; font-weight: bold; color: #e0e0e0; margin-top: 10px;")

        except ValueError:
            self.lbl_total_cost.setText("Error: Ingrese valores numéricos válidos")
            self.lbl_total_cost.setStyleSheet("font-size: 16px; font-weight: bold; color: #8b0000;")
            self.lbl_sale_price.setText("")
