from flask import Blueprint, jsonify, request
from flask_restful import Api, Resource
from app.models.alert_config import AlertConfig
from app.models.report_schedule import ReportSchedule
from app.utils.reports import generate_metrics_pdf, generate_metrics_csv
from app.tasks.reporting import collect_metrics_data
from app.utils.logger import log_error
from datetime import datetime
import os

bp = Blueprint('metrics_api', __name__)
api = Api(bp)

class MetricsAPI(Resource):
    """API REST pour les métriques système"""
    
    def get(self):
        """Récupère les métriques actuelles"""
        try:
            metrics = collect_metrics_data({
                'system': ['cpu', 'memory', 'disk'],
                'application': ['users', 'tasks']
            })
            return jsonify(metrics)
        except Exception as e:
            log_error(current_app, f"Erreur API métriques: {str(e)}")
            return {'error': str(e)}, 500

class AlertConfigAPI(Resource):
    """API REST pour la configuration des alertes"""
    
    def get(self):
        """Liste toutes les configurations d'alerte"""
        try:
            alerts = AlertConfig.query.all()
            return jsonify([{
                'id': alert.id,
                'name': alert.name,
                'metric': alert.metric,
                'threshold': alert.threshold,
                'comparison': alert.comparison,
                'severity': alert.severity,
                'enabled': alert.enabled
            } for alert in alerts])
        except Exception as e:
            return {'error': str(e)}, 500
    
    def post(self):
        """Crée une nouvelle configuration d'alerte"""
        try:
            data = request.get_json()
            alert = AlertConfig(
                name=data['name'],
                metric=data['metric'],
                threshold=data['threshold'],
                comparison=data['comparison'],
                severity=data['severity'],
                notification_method=data['notification_method'],
                user_id=data['user_id']
            )
            db.session.add(alert)
            db.session.commit()
            return {'id': alert.id, 'message': 'Alert configuration created'}, 201
        except Exception as e:
            return {'error': str(e)}, 400

class ReportScheduleAPI(Resource):
    """API REST pour la programmation des rapports"""
    
    def get(self):
        """Liste toutes les programmations de rapports"""
        try:
            schedules = ReportSchedule.query.all()
            return jsonify([{
                'id': schedule.id,
                'name': schedule.name,
                'frequency': schedule.frequency,
                'format': schedule.format,
                'notification_method': schedule.notification_method,
                'enabled': schedule.enabled,
                'last_run': schedule.last_run.isoformat() if schedule.last_run else None
            } for schedule in schedules])
        except Exception as e:
            return {'error': str(e)}, 500
    
    def post(self):
        """Crée une nouvelle programmation de rapport"""
        try:
            data = request.get_json()
            schedule = ReportSchedule(
                name=data['name'],
                description=data.get('description'),
                frequency=data['frequency'],
                time=datetime.strptime(data['time'], '%H:%M').time(),
                day_of_week=data.get('day_of_week'),
                day_of_month=data.get('day_of_month'),
                format=data['format'],
                metrics=data['metrics'],
                notification_method=data['notification_method'],
                email=data.get('email'),
                slack_channel=data.get('slack_channel'),
                teams_webhook=data.get('teams_webhook'),
                user_id=data['user_id']
            )
            db.session.add(schedule)
            db.session.commit()
            return {'id': schedule.id, 'message': 'Report schedule created'}, 201
        except Exception as e:
            return {'error': str(e)}, 400

class ExportAPI(Resource):
    """API REST pour l'export des métriques"""
    
    def post(self):
        """Génère un export des métriques"""
        try:
            data = request.get_json()
            metrics_data = collect_metrics_data(data.get('metrics', {}))
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M')
            format = data.get('format', 'pdf')
            
            if format == 'pdf':
                filename = f'export_{timestamp}.pdf'
                filepath = os.path.join(current_app.config['PDF_EXPORT_DIR'], filename)
                generate_metrics_pdf(metrics_data, filepath)
            else:
                filename = f'export_{timestamp}.csv'
                filepath = os.path.join(current_app.config['CSV_EXPORT_DIR'], filename)
                generate_metrics_csv(metrics_data, filepath)
            
            return {
                'message': 'Export generated',
                'filename': filename,
                'path': filepath
            }, 200
        except Exception as e:
            return {'error': str(e)}, 500

# Enregistrement des ressources
api.add_resource(MetricsAPI, '/metrics')
api.add_resource(AlertConfigAPI, '/alerts')
api.add_resource(ReportScheduleAPI, '/schedules')
api.add_resource(ExportAPI, '/export')
