import os
from datetime import timedelta
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv()

class Config:
    # Configuration de base
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-agritech-pro-2025'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///agritech.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuration du serveur
    DEBUG = True
    TESTING = False
    
    # Configuration de l'application
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app', 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # Configuration de la session
    PERMANENT_SESSION_LIFETIME = timedelta(days=31)
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Configuration des templates
    TEMPLATES_AUTO_RELOAD = True
