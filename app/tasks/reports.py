from app import celery_app
from app.models.field import Field
from app.models.task import Task
from app.models.weather_data import WeatherData
from flask import render_template
from flask_mail import Message
from app import mail, db
from datetime import datetime, timedelta
import csv
import io

@celery_app.task
def generate_weekly_report(user_id):
    """Génère un rapport hebdomadaire pour un utilisateur"""
    try:
        # Récupérer les données de la semaine
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=7)
        
        # Récupérer les champs de l'utilisateur
        fields = Field.query.filter_by(user_id=user_id).all()
        
        # Préparer les données du rapport
        report_data = {
            'fields': [],
            'tasks': [],
            'weather': []
        }
        
        for field in fields:
            # Données des champs
            field_data = {
                'name': field.name,
                'area': field.area,
                'crop_type': field.crop_type,
                'status': field.status
            }
            report_data['fields'].append(field_data)
            
            # Tâches associées au champ
            tasks = Task.query.filter_by(
                field_id=field.id,
                created_at=lambda: start_date <= created_at <= end_date
            ).all()
            
            for task in tasks:
                task_data = {
                    'field': field.name,
                    'title': task.title,
                    'status': task.status,
                    'due_date': task.due_date
                }
                report_data['tasks'].append(task_data)
            
            # Données météo
            weather_data = WeatherData.query.filter_by(
                field_id=field.id,
                timestamp=lambda: start_date <= timestamp <= end_date
            ).all()
            
            for weather in weather_data:
                weather_info = {
                    'field': field.name,
                    'temperature': weather.temperature,
                    'humidity': weather.humidity,
                    'timestamp': weather.timestamp
                }
                report_data['weather'].append(weather_info)
        
        # Générer le CSV
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Écrire les données des champs
        writer.writerow(['Champs'])
        writer.writerow(['Nom', 'Surface', 'Culture', 'Statut'])
        for field in report_data['fields']:
            writer.writerow([
                field['name'],
                field['area'],
                field['crop_type'],
                field['status']
            ])
        
        writer.writerow([])  # Ligne vide pour séparer
        
        # Écrire les données des tâches
        writer.writerow(['Tâches'])
        writer.writerow(['Champ', 'Titre', 'Statut', 'Date d\'échéance'])
        for task in report_data['tasks']:
            writer.writerow([
                task['field'],
                task['title'],
                task['status'],
                task['due_date'].strftime('%Y-%m-%d')
            ])
        
        writer.writerow([])
        
        # Écrire les données météo
        writer.writerow(['Données météo'])
        writer.writerow(['Champ', 'Température', 'Humidité', 'Date'])
        for weather in report_data['weather']:
            writer.writerow([
                weather['field'],
                weather['temperature'],
                weather['humidity'],
                weather['timestamp'].strftime('%Y-%m-%d %H:%M')
            ])
        
        # Envoyer le rapport par email
        msg = Message(
            'Rapport hebdomadaire AgriTechPro',
            sender=current_app.config['MAIL_DEFAULT_SENDER'],
            recipients=[user.email]
        )
        
        msg.body = """
        Bonjour,
        
        Veuillez trouver ci-joint votre rapport hebdomadaire AgriTechPro.
        
        Cordialement,
        L'équipe AgriTechPro
        """
        
        msg.attach(
            "rapport_hebdomadaire.csv",
            "text/csv",
            output.getvalue()
        )
        
        mail.send(msg)
        
        return f"Rapport généré et envoyé à {user.email}"
        
    except Exception as e:
        current_app.logger.error(f"Erreur lors de la génération du rapport: {str(e)}")
        return f"Erreur lors de la génération du rapport: {str(e)}"
