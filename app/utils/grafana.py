from grafana_api.grafana_face import GrafanaFace
from app.utils.logger import log_error, log_info
from flask import current_app

def setup_grafana_dashboard():
    """Configure le tableau de bord Grafana"""
    try:
        grafana = GrafanaFace(
            auth=(current_app.config['GRAFANA_USER'], current_app.config['GRAFANA_PASSWORD']),
            host=current_app.config['GRAFANA_URL']
        )
        
        # Créer la source de données InfluxDB
        datasource = {
            "name": "AgriTechPro Metrics",
            "type": "influxdb",
            "url": current_app.config['INFLUXDB_URL'],
            "access": "proxy",
            "basicAuth": False,
            "isDefault": True,
            "jsonData": {
                "defaultBucket": current_app.config['INFLUXDB_BUCKET'],
                "organization": current_app.config['INFLUXDB_ORG'],
                "version": "Flux"
            },
            "secureJsonData": {
                "token": current_app.config['INFLUXDB_TOKEN']
            }
        }
        
        grafana.datasource.create_datasource(datasource)
        
        # Créer le tableau de bord
        dashboard = {
            "dashboard": {
                "id": None,
                "title": "AgriTechPro Monitoring",
                "tags": ["agritechpro", "monitoring"],
                "timezone": "browser",
                "panels": [
                    # Panneau CPU
                    {
                        "title": "CPU Usage",
                        "type": "gauge",
                        "gridPos": {"h": 8, "w": 8, "x": 0, "y": 0},
                        "targets": [{
                            "query": 'from(bucket: "monitoring")\n'
                                   '|> range(start: -5m)\n'
                                   '|> filter(fn: (r) => r["_measurement"] == "system_metrics")\n'
                                   '|> filter(fn: (r) => r["_field"] == "cpu_percent")\n'
                                   '|> last()'
                        }],
                        "fieldConfig": {
                            "defaults": {
                                "thresholds": {
                                    "steps": [
                                        {"value": None, "color": "green"},
                                        {"value": 70, "color": "yellow"},
                                        {"value": 85, "color": "red"}
                                    ]
                                },
                                "max": 100
                            }
                        }
                    },
                    # Panneau Mémoire
                    {
                        "title": "Memory Usage",
                        "type": "gauge",
                        "gridPos": {"h": 8, "w": 8, "x": 8, "y": 0},
                        "targets": [{
                            "query": 'from(bucket: "monitoring")\n'
                                   '|> range(start: -5m)\n'
                                   '|> filter(fn: (r) => r["_measurement"] == "system_metrics")\n'
                                   '|> filter(fn: (r) => r["_field"] == "memory_percent")\n'
                                   '|> last()'
                        }]
                    },
                    # Panneau Utilisateurs Actifs
                    {
                        "title": "Active Users",
                        "type": "graph",
                        "gridPos": {"h": 8, "w": 16, "x": 0, "y": 8},
                        "targets": [{
                            "query": 'from(bucket: "monitoring")\n'
                                   '|> range(start: -24h)\n'
                                   '|> filter(fn: (r) => r["_measurement"] == "app_metrics")\n'
                                   '|> filter(fn: (r) => r["_field"] == "active_users")'
                        }]
                    },
                    # Panneau Anomalies
                    {
                        "title": "Detected Anomalies",
                        "type": "table",
                        "gridPos": {"h": 8, "w": 24, "x": 0, "y": 16},
                        "targets": [{
                            "query": 'from(bucket: "monitoring")\n'
                                   '|> range(start: -24h)\n'
                                   '|> filter(fn: (r) => r["_measurement"] == "log_anomalies")'
                        }]
                    }
                ]
            }
        }
        
        grafana.dashboard.update_dashboard(dashboard)
        log_info(current_app, "Dashboard Grafana configuré avec succès")
        return True
        
    except Exception as e:
        log_error(current_app, f"Erreur lors de la configuration Grafana: {str(e)}")
        return False

def get_dashboard_url():
    """Retourne l'URL du tableau de bord Grafana"""
    try:
        grafana = GrafanaFace(
            auth=(current_app.config['GRAFANA_USER'], current_app.config['GRAFANA_PASSWORD']),
            host=current_app.config['GRAFANA_URL']
        )
        
        dashboard = grafana.dashboard.get_dashboard("agritechpro-monitoring")
        return f"{current_app.config['GRAFANA_URL']}/d/{dashboard['dashboard']['uid']}"
        
    except Exception as e:
        log_error(current_app, f"Erreur lors de la récupération de l'URL Grafana: {str(e)}")
        return None
