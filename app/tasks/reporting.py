from app.celery_app import celery
from app.utils.reports import generate_metrics_pdf, generate_metrics_csv
from app.utils.logger import log_info, log_error
from app.models.user import User
from app.models.report_schedule import ReportSchedule
from datetime import datetime
import os
from flask import current_app
import json

@celery.task
def generate_scheduled_reports():
    """Génère les rapports programmés"""
    try:
        schedules = ReportSchedule.get_due_schedules()
        
        for schedule in schedules:
            try:
                # Collecter les métriques
                metrics_data = collect_metrics_data(schedule.metrics)
                
                # Générer les rapports selon le format
                timestamp = datetime.now().strftime('%Y%m%d_%H%M')
                if schedule.format == 'pdf' or schedule.format == 'both':
                    pdf_path = os.path.join(
                        current_app.config['PDF_EXPORT_DIR'],
                        f'report_{schedule.name}_{timestamp}.pdf'
                    )
                    generate_metrics_pdf(metrics_data, pdf_path)
                
                if schedule.format == 'csv' or schedule.format == 'both':
                    csv_path = os.path.join(
                        current_app.config['CSV_EXPORT_DIR'],
                        f'report_{schedule.name}_{timestamp}.csv'
                    )
                    generate_metrics_csv(metrics_data, csv_path)
                
                # Envoyer les notifications
                if schedule.notification_method == 'email':
                    send_report_email.delay(schedule.user_id, pdf_path if schedule.format != 'csv' else csv_path)
                elif schedule.notification_method == 'slack':
                    send_slack_report.delay(schedule.slack_channel, pdf_path if schedule.format != 'csv' else csv_path)
                elif schedule.notification_method == 'teams':
                    send_teams_report.delay(schedule.teams_webhook, pdf_path if schedule.format != 'csv' else csv_path)
                
                # Mettre à jour la dernière exécution
                schedule.update_last_run()
                
            except Exception as e:
                log_error(current_app, f"Erreur pour le rapport {schedule.name}: {str(e)}")
                continue
        
        return "Génération des rapports programmés terminée"
        
    except Exception as e:
        log_error(current_app, f"Erreur lors de la génération des rapports: {str(e)}")
        return f"Erreur: {str(e)}"

@celery.task
def send_slack_report(channel, file_path):
    """Envoie un rapport via Slack"""
    try:
        from slack_sdk import WebClient
        from slack_sdk.errors import SlackApiError
        
        client = WebClient(token=current_app.config['SLACK_BOT_TOKEN'])
        
        # Upload du fichier
        with open(file_path, 'rb') as file:
            response = client.files_upload(
                channels=channel,
                file=file,
                title="Rapport de monitoring AgriTechPro",
                initial_comment="Voici votre rapport de monitoring programmé :"
            )
        
        if response['ok']:
            log_info(current_app, f"Rapport envoyé sur Slack: {channel}")
            return f"Rapport envoyé sur Slack: {channel}"
        else:
            raise Exception("Erreur lors de l'envoi Slack")
            
    except Exception as e:
        log_error(current_app, f"Erreur lors de l'envoi Slack: {str(e)}")
        return f"Erreur Slack: {str(e)}"

@celery.task
def send_teams_report(webhook_url, file_path):
    """Envoie un rapport via Microsoft Teams"""
    try:
        import requests
        
        # Créer le message Teams
        message = {
            "type": "message",
            "attachments": [{
                "contentType": "application/vnd.microsoft.card.adaptive",
                "contentUrl": None,
                "content": {
                    "type": "AdaptiveCard",
                    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                    "version": "1.2",
                    "body": [{
                        "type": "TextBlock",
                        "text": "Rapport de monitoring AgriTechPro",
                        "weight": "bolder",
                        "size": "large"
                    }, {
                        "type": "TextBlock",
                        "text": "Voici votre rapport de monitoring programmé.",
                        "wrap": True
                    }]
                }
            }]
        }
        
        # Envoyer le message
        response = requests.post(webhook_url, json=message)
        
        if response.status_code == 200:
            # Upload du fichier (via autre méthode car Teams Webhook ne supporte pas les fichiers directement)
            file_url = upload_to_storage(file_path)  # Implémenter cette fonction selon vos besoins
            
            # Envoyer le lien du fichier
            message["attachments"][0]["content"]["body"].append({
                "type": "TextBlock",
                "text": f"[Télécharger le rapport]({file_url})",
                "wrap": True
            })
            
            requests.post(webhook_url, json=message)
            
            log_info(current_app, "Rapport envoyé sur Teams")
            return "Rapport envoyé sur Teams"
        else:
            raise Exception(f"Erreur Teams: {response.status_code}")
            
    except Exception as e:
        log_error(current_app, f"Erreur lors de l'envoi Teams: {str(e)}")
        return f"Erreur Teams: {str(e)}"

def collect_metrics_data(metrics_config):
    """Collecte les métriques selon la configuration"""
    try:
        metrics = json.loads(metrics_config)
        data = {}
        
        # Métriques système
        if 'system' in metrics:
            import psutil
            if 'cpu' in metrics['system']:
                data['cpu_percent'] = psutil.cpu_percent()
            if 'memory' in metrics['system']:
                data['memory_percent'] = psutil.virtual_memory().percent
            if 'disk' in metrics['system']:
                data['disk_percent'] = psutil.disk_usage('/').percent
        
        # Métriques application
        if 'application' in metrics:
            if 'users' in metrics['application']:
                from app.models.user import User
                data['total_users'] = User.query.count()
                data['active_users'] = User.query.filter(
                    User.last_seen >= datetime.utcnow() - datetime.timedelta(hours=24)
                ).count()
            if 'tasks' in metrics['application']:
                from app.models.task import Task
                data['total_tasks'] = Task.query.count()
                data['pending_tasks'] = Task.query.filter_by(status='pending').count()
        
        # Métriques personnalisées
        if 'custom' in metrics:
            # Implémenter la collecte de métriques personnalisées ici
            pass
        
        return data
        
    except Exception as e:
        log_error(current_app, f"Erreur lors de la collecte des métriques: {str(e)}")
        return {}
