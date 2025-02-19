import os
import psutil
import shutil
import tempfile
from datetime import datetime, timedelta
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway
from pywebpush import webpush, WebPushException
from app import celery_app, db
from app.models.user import User
from app.utils.logger import log_info, log_error
from flask import current_app

@celery_app.task
def cleanup_temp_files():
    """Nettoie les fichiers temporaires"""
    try:
        # Répertoires à nettoyer
        cleanup_dirs = [
            os.path.join(current_app.root_path, 'static', 'temp'),
            os.path.join(current_app.root_path, 'static', 'uploads', 'temp'),
            tempfile.gettempdir()
        ]
        
        total_cleaned = 0
        for directory in cleanup_dirs:
            if os.path.exists(directory):
                # Supprimer les fichiers plus vieux que 24h
                cutoff = datetime.now().timestamp() - 86400
                
                for filename in os.listdir(directory):
                    filepath = os.path.join(directory, filename)
                    try:
                        if os.path.getctime(filepath) < cutoff:
                            if os.path.isfile(filepath):
                                os.remove(filepath)
                            elif os.path.isdir(filepath):
                                shutil.rmtree(filepath)
                            total_cleaned += 1
                    except Exception as e:
                        log_error(current_app, f"Erreur lors de la suppression de {filepath}: {str(e)}")
        
        log_info(current_app, f"Nettoyage terminé: {total_cleaned} fichiers supprimés")
        return f"Nettoyage terminé: {total_cleaned} fichiers supprimés"
        
    except Exception as e:
        log_error(current_app, f"Erreur lors du nettoyage des fichiers temporaires: {str(e)}")
        return f"Erreur lors du nettoyage: {str(e)}"

@celery_app.task
def monitor_system_performance():
    """Surveille les performances système"""
    try:
        # Créer un nouveau registre
        registry = CollectorRegistry()
        
        # Métriques système
        cpu_gauge = Gauge('system_cpu_percent', 'CPU usage in percent', registry=registry)
        memory_gauge = Gauge('system_memory_percent', 'Memory usage in percent', registry=registry)
        disk_gauge = Gauge('system_disk_percent', 'Disk usage in percent', registry=registry)
        
        # Métriques application
        db_size_gauge = Gauge('app_database_size_mb', 'Database size in MB', registry=registry)
        active_users_gauge = Gauge('app_active_users', 'Number of active users', registry=registry)
        
        # Collecter les métriques
        cpu_gauge.set(psutil.cpu_percent())
        memory_gauge.set(psutil.virtual_memory().percent)
        disk_gauge.set(psutil.disk_usage('/').percent)
        
        # Taille de la base de données
        db_path = current_app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        db_size = os.path.getsize(db_path) / (1024 * 1024)  # Convertir en MB
        db_size_gauge.set(db_size)
        
        # Utilisateurs actifs (connectés dans les dernières 24h)
        active_users = User.query.filter(
            User.last_seen >= datetime.utcnow() - timedelta(hours=24)
        ).count()
        active_users_gauge.set(active_users)
        
        # Envoyer à Prometheus si configuré
        if current_app.config.get('PROMETHEUS_PUSHGATEWAY'):
            push_to_gateway(
                current_app.config['PROMETHEUS_PUSHGATEWAY'],
                job='agritechpro_metrics',
                registry=registry
            )
        
        # Vérifier les seuils d'alerte
        alerts = []
        if psutil.cpu_percent() > 80:
            alerts.append("CPU usage high (>80%)")
        if psutil.virtual_memory().percent > 85:
            alerts.append("Memory usage high (>85%)")
        if psutil.disk_usage('/').percent > 90:
            alerts.append("Disk usage critical (>90%)")
            
        # Envoyer des alertes si nécessaire
        if alerts:
            send_system_alerts.delay(alerts)
        
        log_info(current_app, "Monitoring système effectué")
        return "Monitoring système effectué"
        
    except Exception as e:
        log_error(current_app, f"Erreur lors du monitoring système: {str(e)}")
        return f"Erreur lors du monitoring: {str(e)}"

@celery_app.task
def send_system_alerts(alerts):
    """Envoie des alertes système via Web Push"""
    try:
        # Récupérer les administrateurs
        admins = User.query.filter_by(is_admin=True).all()
        
        for admin in admins:
            if admin.push_subscription:
                try:
                    webpush(
                        subscription_info=json.loads(admin.push_subscription),
                        data=json.dumps({
                            "title": "Alerte Système AgriTechPro",
                            "body": "\n".join(alerts),
                            "icon": "/static/img/logo.png"
                        }),
                        vapid_private_key=current_app.config['VAPID_PRIVATE_KEY'],
                        vapid_claims={
                            "sub": "mailto:admin@agritechpro.com"
                        }
                    )
                except WebPushException as e:
                    log_error(current_app, f"Erreur d'envoi Push à {admin.email}: {str(e)}")
                    
        return f"Alertes envoyées à {len(admins)} administrateurs"
        
    except Exception as e:
        log_error(current_app, f"Erreur lors de l'envoi des alertes: {str(e)}")
        return f"Erreur lors de l'envoi des alertes: {str(e)}"
