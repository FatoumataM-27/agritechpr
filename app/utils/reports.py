from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import csv
import io
from datetime import datetime
from app.models.alert_config import AlertConfig
from app.utils.logger import log_error

def generate_metrics_pdf(metrics_data, filename):
    """Génère un rapport PDF des métriques système"""
    try:
        doc = SimpleDocTemplate(filename, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []
        
        # Titre
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30
        )
        elements.append(Paragraph("Rapport de Monitoring AgriTechPro", title_style))
        elements.append(Spacer(1, 12))
        
        # Date du rapport
        date_style = ParagraphStyle(
            'DateStyle',
            parent=styles['Normal'],
            fontSize=12,
            spaceAfter=30
        )
        elements.append(Paragraph(f"Généré le : {datetime.now().strftime('%Y-%m-%d %H:%M')}", date_style))
        elements.append(Spacer(1, 20))
        
        # Métriques système
        elements.append(Paragraph("Métriques Système", styles['Heading2']))
        system_data = [
            ['Métrique', 'Valeur', 'Statut'],
            ['CPU', f"{metrics_data['cpu_percent']}%", get_status(metrics_data['cpu_percent'], 80)],
            ['Mémoire', f"{metrics_data['memory_percent']}%", get_status(metrics_data['memory_percent'], 85)],
            ['Disque', f"{metrics_data['disk_percent']}%", get_status(metrics_data['disk_percent'], 90)]
        ]
        system_table = Table(system_data, colWidths=[2*inch, 1.5*inch, 1.5*inch])
        style_table(system_table)
        elements.append(system_table)
        elements.append(Spacer(1, 20))
        
        # Métriques application
        elements.append(Paragraph("Métriques Application", styles['Heading2']))
        app_data = [
            ['Métrique', 'Valeur'],
            ['Utilisateurs Actifs', metrics_data['active_users']],
            ['Total Champs', metrics_data['total_fields']],
            ['Tâches en Cours', metrics_data['pending_tasks']]
        ]
        app_table = Table(app_data, colWidths=[2*inch, 1.5*inch])
        style_table(app_table)
        elements.append(app_table)
        elements.append(Spacer(1, 20))
        
        # Anomalies détectées
        if metrics_data.get('anomalies'):
            elements.append(Paragraph("Anomalies Détectées", styles['Heading2']))
            anomaly_data = [['Timestamp', 'Type', 'Description']]
            for anomaly in metrics_data['anomalies']:
                anomaly_data.append([
                    anomaly['timestamp'],
                    anomaly['type'],
                    anomaly['description']
                ])
            anomaly_table = Table(anomaly_data, colWidths=[1.5*inch, 1.5*inch, 3*inch])
            style_table(anomaly_table)
            elements.append(anomaly_table)
        
        doc.build(elements)
        return True
        
    except Exception as e:
        log_error(current_app, f"Erreur lors de la génération du PDF: {str(e)}")
        return False

def generate_metrics_csv(metrics_data, filename):
    """Génère un fichier CSV des métriques système"""
    try:
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            
            # En-têtes
            writer.writerow(['Catégorie', 'Métrique', 'Valeur', 'Timestamp'])
            
            # Métriques système
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            system_metrics = [
                ['Système', 'CPU', f"{metrics_data['cpu_percent']}%", timestamp],
                ['Système', 'Mémoire', f"{metrics_data['memory_percent']}%", timestamp],
                ['Système', 'Disque', f"{metrics_data['disk_percent']}%", timestamp]
            ]
            writer.writerows(system_metrics)
            
            # Métriques application
            app_metrics = [
                ['Application', 'Utilisateurs Actifs', metrics_data['active_users'], timestamp],
                ['Application', 'Total Champs', metrics_data['total_fields'], timestamp],
                ['Application', 'Tâches en Cours', metrics_data['pending_tasks'], timestamp]
            ]
            writer.writerows(app_metrics)
            
            # Anomalies
            if metrics_data.get('anomalies'):
                for anomaly in metrics_data['anomalies']:
                    writer.writerow([
                        'Anomalie',
                        anomaly['type'],
                        anomaly['description'],
                        anomaly['timestamp']
                    ])
                    
        return True
        
    except Exception as e:
        log_error(current_app, f"Erreur lors de la génération du CSV: {str(e)}")
        return False

def get_status(value, threshold):
    """Retourne le statut en fonction de la valeur et du seuil"""
    if value >= threshold:
        return 'CRITIQUE'
    elif value >= threshold * 0.8:
        return 'ATTENTION'
    return 'NORMAL'

def style_table(table):
    """Applique un style à une table"""
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 12),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ])
    table.setStyle(style)
