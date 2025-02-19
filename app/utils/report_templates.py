from jinja2 import Template
from datetime import datetime
import json
import os
from flask import current_app
from weasyprint import HTML, CSS
from app.utils.logger import log_info, log_error

class ReportTemplate:
    """Classe de base pour les templates de rapport"""
    
    def __init__(self, title, description=None):
        self.title = title
        self.description = description
        self.created_at = datetime.now()
        self.sections = []
        
    def add_section(self, title, content):
        """Ajoute une section au rapport"""
        self.sections.append({
            'title': title,
            'content': content
        })
        
    def get_context(self):
        """Retourne le contexte pour le template"""
        return {
            'title': self.title,
            'description': self.description,
            'created_at': self.created_at,
            'sections': self.sections
        }

class PDFReportTemplate(ReportTemplate):
    """Template pour les rapports PDF"""
    
    def __init__(self, title, description=None):
        super().__init__(title, description)
        self.css = self._get_default_css()
        
    def _get_default_css(self):
        """Retourne le CSS par défaut pour les rapports PDF"""
        return CSS(string='''
            @page {
                size: A4;
                margin: 2.5cm;
                @top-center {
                    content: "AgriTechPro - Rapport de Monitoring";
                    font-size: 9pt;
                    color: #666;
                }
                @bottom-center {
                    content: "Page " counter(page) " sur " counter(pages);
                    font-size: 9pt;
                }
            }
            body {
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
            }
            h1 {
                color: #2ECC71;
                border-bottom: 2px solid #2ECC71;
                padding-bottom: 0.5em;
            }
            h2 {
                color: #27AE60;
                margin-top: 1.5em;
            }
            .metric {
                background: #f8f9fa;
                padding: 1em;
                margin: 0.5em 0;
                border-radius: 4px;
            }
            .chart {
                width: 100%;
                max-width: 800px;
                margin: 1em auto;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin: 1em 0;
            }
            th, td {
                padding: 0.5em;
                border: 1px solid #ddd;
            }
            th {
                background: #2ECC71;
                color: white;
            }
            tr:nth-child(even) {
                background: #f8f9fa;
            }
        ''')
    
    def generate(self, output_path):
        """Génère le rapport PDF"""
        try:
            template_str = '''
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>{{ title }}</title>
            </head>
            <body>
                <h1>{{ title }}</h1>
                {% if description %}
                <p>{{ description }}</p>
                {% endif %}
                
                <div class="metadata">
                    <p>Généré le : {{ created_at.strftime('%d/%m/%Y à %H:%M') }}</p>
                </div>
                
                {% for section in sections %}
                <section>
                    <h2>{{ section.title }}</h2>
                    {{ section.content|safe }}
                </section>
                {% endfor %}
            </body>
            </html>
            '''
            
            template = Template(template_str)
            html_content = template.render(**self.get_context())
            
            HTML(string=html_content).write_pdf(
                output_path,
                stylesheets=[self.css]
            )
            
            log_info(current_app, f"Rapport PDF généré : {output_path}")
            return True
            
        except Exception as e:
            log_error(current_app, f"Erreur lors de la génération du PDF : {str(e)}")
            return False

class CSVReportTemplate(ReportTemplate):
    """Template pour les rapports CSV"""
    
    def generate(self, output_path):
        """Génère le rapport CSV"""
        try:
            import csv
            
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # En-tête
                writer.writerow(['Rapport', self.title])
                writer.writerow(['Date de génération', self.created_at.strftime('%d/%m/%Y %H:%M')])
                writer.writerow([])
                
                # Sections
                for section in self.sections:
                    writer.writerow([section['title']])
                    
                    # Si le contenu est un dictionnaire ou une liste
                    if isinstance(section['content'], (dict, list)):
                        data = section['content']
                        if isinstance(data, dict):
                            for key, value in data.items():
                                writer.writerow([key, value])
                        else:
                            for item in data:
                                if isinstance(item, dict):
                                    writer.writerow(item.keys())
                                    writer.writerow(item.values())
                                else:
                                    writer.writerow([item])
                    else:
                        writer.writerow([section['content']])
                    
                    writer.writerow([])  # Ligne vide entre les sections
            
            log_info(current_app, f"Rapport CSV généré : {output_path}")
            return True
            
        except Exception as e:
            log_error(current_app, f"Erreur lors de la génération du CSV : {str(e)}")
            return False

def create_system_report(metrics_data, format='pdf'):
    """Crée un rapport système avec les métriques fournies"""
    title = "Rapport de Monitoring Système"
    description = "Vue d'ensemble des métriques système et de l'application"
    
    if format == 'pdf':
        template = PDFReportTemplate(title, description)
    else:
        template = CSVReportTemplate(title, description)
    
    # Section Métriques Système
    system_metrics = {
        'CPU (%)': metrics_data.get('cpu_percent', 'N/A'),
        'Mémoire (%)': metrics_data.get('memory_percent', 'N/A'),
        'Disque (%)': metrics_data.get('disk_percent', 'N/A')
    }
    template.add_section("Métriques Système", system_metrics)
    
    # Section Application
    app_metrics = {
        'Utilisateurs Total': metrics_data.get('total_users', 'N/A'),
        'Utilisateurs Actifs': metrics_data.get('active_users', 'N/A'),
        'Tâches en Attente': metrics_data.get('pending_tasks', 'N/A')
    }
    template.add_section("Métriques Application", app_metrics)
    
    # Section Performances
    if 'performance' in metrics_data:
        perf_metrics = {
            'Temps de Réponse Moyen': f"{metrics_data['performance'].get('avg_response_time', 'N/A')} ms",
            'Requêtes par Minute': metrics_data['performance'].get('requests_per_minute', 'N/A'),
            'Erreurs par Minute': metrics_data['performance'].get('errors_per_minute', 'N/A')
        }
        template.add_section("Performances", perf_metrics)
    
    return template

def create_custom_report(title, sections, format='pdf'):
    """Crée un rapport personnalisé avec les sections fournies"""
    if format == 'pdf':
        template = PDFReportTemplate(title)
    else:
        template = CSVReportTemplate(title)
    
    for section in sections:
        template.add_section(section['title'], section['content'])
    
    return template
