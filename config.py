import os
from dotenv import load_dotenv
from datetime import timedelta
from celery.schedules import crontab

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-agritech-pro-2025'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'agritech.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuration email
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    # Configuration de l'application
    FIELDS_PER_PAGE = 10
    TASKS_PER_PAGE = 20
    WEATHER_API_KEY = os.environ.get('WEATHER_API_KEY')
    
    # Configuration de sécurité
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    
    # Configuration AWS S3
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    AWS_BACKUP_BUCKET = os.environ.get('AWS_BACKUP_BUCKET')
    
    # Configuration Prometheus
    PROMETHEUS_PUSHGATEWAY = os.environ.get('PROMETHEUS_PUSHGATEWAY')
    
    # Configuration Web Push
    VAPID_PUBLIC_KEY = os.environ.get('VAPID_PUBLIC_KEY')
    VAPID_PRIVATE_KEY = os.environ.get('VAPID_PRIVATE_KEY')
    VAPID_CLAIM_EMAIL = os.environ.get('VAPID_CLAIM_EMAIL', 'admin@agritechpro.com')
    
    # Configuration InfluxDB
    INFLUXDB_URL = os.environ.get('INFLUXDB_URL', 'http://localhost:8086')
    INFLUXDB_TOKEN = os.environ.get('INFLUXDB_TOKEN')
    INFLUXDB_ORG = os.environ.get('INFLUXDB_ORG', 'agritechpro')
    INFLUXDB_BUCKET = os.environ.get('INFLUXDB_BUCKET', 'monitoring')
    
    # Configuration Celery
    CELERY_BROKER_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    CELERY_ACCEPT_CONTENT = ['json']
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_RESULT_SERIALIZER = 'json'
    CELERY_TIMEZONE = 'Europe/Paris'
    
    # Configuration Slack
    SLACK_BOT_TOKEN = os.environ.get('SLACK_BOT_TOKEN')
    SLACK_DEFAULT_CHANNEL = os.environ.get('SLACK_DEFAULT_CHANNEL', '#monitoring')
    
    # Configuration Teams
    TEAMS_WEBHOOK_URL = os.environ.get('TEAMS_WEBHOOK_URL')
    
    # Configuration des rapports programmés
    REPORT_RETENTION_DAYS = 30  # Durée de conservation des rapports en jours
    
    # Configuration des tâches périodiques Celery
    CELERYBEAT_SCHEDULE = {
        'generate-scheduled-reports': {
            'task': 'app.tasks.reporting.generate_scheduled_reports',
            'schedule': crontab(minute='*/15'),  # Every 15 minutes
        },
    }
    
    # Configuration Grafana
    GRAFANA_URL = os.environ.get('GRAFANA_URL', 'http://localhost:3000')
    GRAFANA_USER = os.environ.get('GRAFANA_USER', 'admin')
    GRAFANA_PASSWORD = os.environ.get('GRAFANA_PASSWORD', 'admin')
    
    # Configuration des exports
    PDF_EXPORT_DIR = os.path.join(basedir, 'exports', 'pdf')
    CSV_EXPORT_DIR = os.path.join(basedir, 'exports', 'csv')
    
    # Configuration OpenWeatherMap
    OPENWEATHER_API_KEY = os.environ.get('OPENWEATHER_API_KEY')
    
    # Coordonnées des régions du Sénégal avec données supplémentaires
    REGIONS_COORDINATES = {
        'Dakar': {
            'lat': 14.7167, 
            'lon': -17.4677,
            'description': 'Capitale du Sénégal'
        },
        'Saint-Louis': {
            'lat': 16.0179, 
            'lon': -16.4896,
            'description': 'Ancienne capitale du Sénégal'
        },
        'Tambacounda': {
            'lat': 13.7707, 
            'lon': -13.6673,
            'description': 'Plus grande région du Sénégal'
        },
        'Kaolack': {
            'lat': 14.1667, 
            'lon': -16.0833,
            'description': 'Centre commercial important'
        },
        'Ziguinchor': {
            'lat': 12.5667, 
            'lon': -16.2667,
            'description': 'Capitale de la Casamance'
        },
        'Thiès': {
            'lat': 14.7833, 
            'lon': -16.9333,
            'description': 'Centre industriel majeur'
        },
        'Louga': {
            'lat': 15.6167, 
            'lon': -16.2167,
            'description': 'Zone agricole importante'
        },
        'Diourbel': {
            'lat': 14.6500, 
            'lon': -16.2333,
            'description': 'Centre religieux important'
        },
        'Kolda': {
            'lat': 12.8833, 
            'lon': -14.9500,
            'description': 'Région agricole du sud'
        },
        'Fatick': {
            'lat': 14.3333, 
            'lon': -16.4000,
            'description': 'Zone de production de sel'
        },
        'Matam': {
            'lat': 15.6667, 
            'lon': -13.2500,
            'description': 'Région frontalière avec le Mali'
        },
        'Kaffrine': {
            'lat': 14.1667, 
            'lon': -15.5500,
            'description': 'Zone agricole centrale'
        },
        'Sédhiou': {
            'lat': 12.7000, 
            'lon': -15.5500,
            'description': 'Région de la Casamance'
        },
        'Kédougou': {
            'lat': 12.5500, 
            'lon': -12.1833,
            'description': 'Région minière'
        }
    }
    
    # Création des répertoires d'export
    os.makedirs(PDF_EXPORT_DIR, exist_ok=True)
    os.makedirs(CSV_EXPORT_DIR, exist_ok=True)

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'agritech-dev.db')

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'agritech-test.db')
    WTF_CSRF_ENABLED = False

class ProductionConfig(Config):
    # Correction de l'URL de la base de données pour Heroku
    if os.environ.get('DATABASE_URL'):
        if os.environ.get('DATABASE_URL').startswith('postgres://'):
            SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL').replace('postgres://', 'postgresql://', 1)
    
    # Configuration de sécurité pour la production
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
