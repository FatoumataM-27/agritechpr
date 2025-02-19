import os
from datetime import datetime
import shutil
import boto3
from PIL import Image
from app import celery_app, db
from app.models.user import User
from app.models.field import Field
from app.models.task import Task
from app.utils.logger import log_info, log_error
from flask import current_app

@celery_app.task
def backup_database():
    """Sauvegarde quotidienne de la base de données"""
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir = os.path.join(current_app.root_path, 'backups')
        
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        
        # Backup du fichier SQLite
        db_path = current_app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        backup_path = os.path.join(backup_dir, f'agritech_{timestamp}.db')
        shutil.copy2(db_path, backup_path)
        
        # Upload vers S3 si configuré
        if current_app.config.get('AWS_ACCESS_KEY_ID'):
            s3 = boto3.client(
                's3',
                aws_access_key_id=current_app.config['AWS_ACCESS_KEY_ID'],
                aws_secret_access_key=current_app.config['AWS_SECRET_ACCESS_KEY']
            )
            
            s3.upload_file(
                backup_path,
                current_app.config['AWS_BACKUP_BUCKET'],
                f'database/agritech_{timestamp}.db'
            )
            
            # Nettoyer les vieux backups locaux (garder 7 jours)
            cleanup_old_backups.delay(backup_dir, days=7)
            
        log_info(current_app, f"Backup de la base de données créé: {backup_path}")
        return f"Backup créé avec succès: {backup_path}"
        
    except Exception as e:
        log_error(current_app, f"Erreur lors du backup: {str(e)}")
        return f"Erreur lors du backup: {str(e)}"

@celery_app.task
def cleanup_old_backups(backup_dir, days=7):
    """Nettoie les vieux fichiers de backup"""
    try:
        cutoff = datetime.now().timestamp() - (days * 86400)
        
        for filename in os.listdir(backup_dir):
            filepath = os.path.join(backup_dir, filename)
            if os.path.getctime(filepath) < cutoff:
                os.remove(filepath)
                log_info(current_app, f"Ancien backup supprimé: {filepath}")
                
    except Exception as e:
        log_error(current_app, f"Erreur lors du nettoyage des backups: {str(e)}")

@celery_app.task
def optimize_images(field_id=None):
    """Optimise les images uploadées"""
    try:
        upload_dir = os.path.join(current_app.root_path, 'static', 'uploads')
        
        if field_id:
            # Optimiser les images d'un champ spécifique
            field_dir = os.path.join(upload_dir, f'field_{field_id}')
            if os.path.exists(field_dir):
                optimize_directory_images(field_dir)
        else:
            # Optimiser toutes les images
            for root, dirs, files in os.walk(upload_dir):
                optimize_directory_images(root)
                
        return "Optimisation des images terminée"
        
    except Exception as e:
        log_error(current_app, f"Erreur lors de l'optimisation des images: {str(e)}")
        return f"Erreur lors de l'optimisation des images: {str(e)}"

def optimize_directory_images(directory):
    """Optimise toutes les images dans un répertoire"""
    for filename in os.listdir(directory):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            filepath = os.path.join(directory, filename)
            try:
                with Image.open(filepath) as img:
                    # Redimensionner si trop grand
                    if img.size[0] > 1920 or img.size[1] > 1080:
                        img.thumbnail((1920, 1080), Image.LANCZOS)
                    
                    # Optimiser et sauvegarder
                    img.save(filepath, optimize=True, quality=85)
                    
                log_info(current_app, f"Image optimisée: {filepath}")
                
            except Exception as e:
                log_error(current_app, f"Erreur lors de l'optimisation de {filepath}: {str(e)}")

@celery_app.task
def generate_usage_statistics():
    """Génère des statistiques d'utilisation"""
    try:
        stats = {
            'users': {
                'total': User.query.count(),
                'active': User.query.filter_by(is_active=True).count(),
                'new_last_30d': User.query.filter(
                    User.created_at >= datetime.now() - timedelta(days=30)
                ).count()
            },
            'fields': {
                'total': Field.query.count(),
                'by_crop_type': {}
            },
            'tasks': {
                'total': Task.query.count(),
                'completed': Task.query.filter_by(status='completed').count(),
                'pending': Task.query.filter_by(status='pending').count()
            }
        }
        
        # Statistiques par type de culture
        for field in Field.query.all():
            crop_type = field.crop_type
            if crop_type in stats['fields']['by_crop_type']:
                stats['fields']['by_crop_type'][crop_type] += 1
            else:
                stats['fields']['by_crop_type'][crop_type] = 1
        
        # Sauvegarder les stats dans la base
        usage_stat = UsageStatistics(
            timestamp=datetime.utcnow(),
            statistics=stats
        )
        db.session.add(usage_stat)
        db.session.commit()
        
        log_info(current_app, "Statistiques d'utilisation générées")
        return "Statistiques générées avec succès"
        
    except Exception as e:
        log_error(current_app, f"Erreur lors de la génération des statistiques: {str(e)}")
        return f"Erreur lors de la génération des statistiques: {str(e)}"
