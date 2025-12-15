from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from datetime import datetime
import os

class ReportGenerator:
    """Generador de informes PDF para Formexa."""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()
    
    def _create_custom_styles(self):
        """Crea estilos personalizados para los informes."""
        self.styles.add(ParagraphStyle(
            name='TitleCustom',
            parent=self.styles['Title'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.HexColor('#2C3E50')
        ))
        
        self.styles.add(ParagraphStyle(
            name='Heading2Custom',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceBefore=20,
            spaceAfter=10,
            textColor=colors.HexColor('#34495E')
        ))
        
        self.styles.add(ParagraphStyle(
            name='NormalCustom',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceAfter=6
        ))
    
    def generate_cost_report(self, data, output_path):
        """Genera un informe detallado de costes de impresión."""
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        elements = []
        
        # Título
        elements.append(Paragraph("Informe de Costes de Impresión", self.styles['TitleCustom']))
        elements.append(Paragraph(f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}", self.styles['NormalCustom']))
        elements.append(Spacer(1, 20))
        
        # Detalles del Proyecto (si existen)
        if 'project_name' in data:
            elements.append(Paragraph("Detalles del Proyecto", self.styles['Heading2Custom']))
            elements.append(Paragraph(f"<b>Nombre:</b> {data['project_name']}", self.styles['NormalCustom']))
            if 'model_name' in data:
                elements.append(Paragraph(f"<b>Modelo:</b> {data['model_name']}", self.styles['NormalCustom']))
            elements.append(Spacer(1, 10))
        
        # Tabla de Parámetros
        elements.append(Paragraph("Parámetros de Impresión", self.styles['Heading2Custom']))
        
        params_data = [
            ["Parámetro", "Valor"],
            ["Peso del Modelo", f"{data.get('weight', 0)} g"],
            ["Tiempo de Impresión", f"{data.get('time', 0)} h"],
            ["Precio Filamento", f"{data.get('price_per_kg', 0)} €/kg"],
            ["Consumo Energía", f"{data.get('power', 0)} W"],
            ["Coste Energía", f"{data.get('energy_cost_rate', 0)} €/kWh"]
        ]
        
        t_params = Table(params_data, colWidths=[3*inch, 3*inch])
        t_params.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (1, 0), colors.HexColor('#34495E')),
            ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ECF0F1')),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(t_params)
        elements.append(Spacer(1, 20))
        
        # Tabla de Costes
        elements.append(Paragraph("Desglose de Costes", self.styles['Heading2Custom']))
        
        costs_data = [
            ["Concepto", "Coste"],
            ["Coste de Filamento", f"{data.get('filament_cost', 0):.2f} €"],
            ["Coste de Energía", f"{data.get('energy_cost', 0):.2f} €"],
            ["COSTE TOTAL", f"{data.get('total_cost', 0):.2f} €"]
        ]
        
        t_costs = Table(costs_data, colWidths=[3*inch, 3*inch])
        t_costs.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (1, 0), colors.HexColor('#27AE60')),
            ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -2), colors.HexColor('#ECF0F1')),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#D5F5E3')),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(t_costs)
        
        # Pie de página
        elements.append(Spacer(1, 40))
        elements.append(Paragraph("Generado por Formexa", self.styles['NormalCustom']))
        
        doc.build(elements)
        return True

    def generate_stats_report(self, user_name, stats, output_path):
        """Genera un informe de estadísticas de proyectos."""
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        elements = []
        
        # Título
        elements.append(Paragraph(f"Informe de Estadísticas - {user_name}", self.styles['TitleCustom']))
        elements.append(Paragraph(f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}", self.styles['NormalCustom']))
        elements.append(Spacer(1, 20))
        
        # Resumen General
        elements.append(Paragraph("Resumen General", self.styles['Heading2Custom']))
        
        summary_data = [
            ["Métrica", "Valor"],
            ["Total Proyectos", str(stats['total_projects'])],
            ["Completados", str(stats['completed'])],
            ["En Progreso", str(stats['in_progress'])],
            ["Pendientes", str(stats['pending'])],
            ["Total Gastado", f"{stats['total_spent']:.2f} €"],
            ["Horas de Impresión", f"{stats['total_hours']:.1f} h"]
        ]
        
        t_summary = Table(summary_data, colWidths=[3*inch, 3*inch])
        t_summary.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (1, 0), colors.HexColor('#8E44AD')),
            ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F4ECF7')),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(t_summary)
        
        # Pie de página
        elements.append(Spacer(1, 40))
        elements.append(Paragraph("Generado por Formexa", self.styles['NormalCustom']))
        
        doc.build(elements)
        return True
