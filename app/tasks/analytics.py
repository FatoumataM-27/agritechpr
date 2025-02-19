import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from datetime import datetime, timedelta
import re
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from app import celery_app
from app.utils.logger import log_info, log_error
from flask import current_app

@celery_app.task
def analyze_logs():
    """Analyse les logs pour détecter les anomalies"""
    try:
        # Lire le fichier de log
        log_entries = []
        with open('logs/agritech.log', 'r') as f:
            for line in f:
                # Parser les logs avec regex
                timestamp_match = re.search(r'\[(.*?)\]', line)
                ip_match = re.search(r'(\d+\.\d+\.\d+\.\d+)', line)
                method_match = re.search(r'(GET|POST|PUT|DELETE)', line)
                status_match = re.search(r'status (\d+)', line)
                
                if all([timestamp_match, ip_match, method_match, status_match]):
                    log_entries.append({
                        'timestamp': datetime.strptime(timestamp_match.group(1), '%Y-%m-%d %H:%M:%S,%f'),
                        'ip': ip_match.group(1),
                        'method': method_match.group(1),
                        'status': int(status_match.group(1))
                    })
        
        if not log_entries:
            return "Aucune entrée de log à analyser"
            
        # Convertir en DataFrame
        df = pd.DataFrame(log_entries)
        
        # Préparer les features pour l'analyse
        df['hour'] = df['timestamp'].dt.hour
        df['minute'] = df['timestamp'].dt.minute
        df['status_class'] = df['status'] // 100
        
        # Encoder les méthodes HTTP
        method_dummies = pd.get_dummies(df['method'], prefix='method')
        features = pd.concat([
            df[['hour', 'minute', 'status_class']],
            method_dummies
        ], axis=1)
        
        # Détecter les anomalies avec Isolation Forest
        clf = IsolationForest(contamination=0.1, random_state=42)
        anomalies = clf.fit_predict(features)
        
        # Identifier les entrées anormales
        anomaly_entries = df[anomalies == -1]
        
        # Sauvegarder les anomalies dans InfluxDB
        save_anomalies_to_influx(anomaly_entries)
        
        # Envoyer des alertes si nécessaire
        if len(anomaly_entries) > 0:
            from app.tasks.system import send_system_alerts
            alerts = [
                f"Détection de {len(anomaly_entries)} anomalies dans les logs",
                f"IPs suspectes: {', '.join(anomaly_entries['ip'].unique())}",
                f"Statuts HTTP anormaux: {', '.join(map(str, anomaly_entries['status'].unique()))}"
            ]
            send_system_alerts.delay(alerts)
        
        return f"Analyse terminée: {len(anomaly_entries)} anomalies détectées"
        
    except Exception as e:
        log_error(current_app, f"Erreur lors de l'analyse des logs: {str(e)}")
        return f"Erreur lors de l'analyse: {str(e)}"

def save_anomalies_to_influx(anomalies):
    """Sauvegarde les anomalies dans InfluxDB"""
    try:
        client = InfluxDBClient(
            url=current_app.config['INFLUXDB_URL'],
            token=current_app.config['INFLUXDB_TOKEN'],
            org=current_app.config['INFLUXDB_ORG']
        )
        
        write_api = client.write_api(write_options=SYNCHRONOUS)
        
        for _, row in anomalies.iterrows():
            point = Point("log_anomalies") \
                .tag("ip", row['ip']) \
                .tag("method", row['method']) \
                .field("status", row['status']) \
                .time(row['timestamp'])
            
            write_api.write(
                bucket=current_app.config['INFLUXDB_BUCKET'],
                record=point
            )
            
        client.close()
        
    except Exception as e:
        log_error(current_app, f"Erreur lors de la sauvegarde dans InfluxDB: {str(e)}")

@celery_app.task
def save_metrics_to_influx():
    """Sauvegarde les métriques système dans InfluxDB"""
    try:
        import psutil
        
        client = InfluxDBClient(
            url=current_app.config['INFLUXDB_URL'],
            token=current_app.config['INFLUXDB_TOKEN'],
            org=current_app.config['INFLUXDB_ORG']
        )
        
        write_api = client.write_api(write_options=SYNCHRONOUS)
        
        # Métriques système
        point = Point("system_metrics") \
            .field("cpu_percent", psutil.cpu_percent()) \
            .field("memory_percent", psutil.virtual_memory().percent) \
            .field("disk_percent", psutil.disk_usage('/').percent)
            
        write_api.write(
            bucket=current_app.config['INFLUXDB_BUCKET'],
            record=point
        )
        
        # Métriques application
        from app.models.user import User
        from app.models.field import Field
        from app.models.task import Task
        
        point = Point("app_metrics") \
            .field("total_users", User.query.count()) \
            .field("active_users", User.query.filter(
                User.last_seen >= datetime.utcnow() - timedelta(hours=24)
            ).count()) \
            .field("total_fields", Field.query.count()) \
            .field("total_tasks", Task.query.count())
            
        write_api.write(
            bucket=current_app.config['INFLUXDB_BUCKET'],
            record=point
        )
        
        client.close()
        
        return "Métriques sauvegardées dans InfluxDB"
        
    except Exception as e:
        log_error(current_app, f"Erreur lors de la sauvegarde des métriques: {str(e)}")
        return f"Erreur lors de la sauvegarde: {str(e)}"
