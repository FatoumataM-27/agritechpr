from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_swagger_ui import get_swaggerui_blueprint
from config import Config
from app.utils.logger import setup_logger
from app.swagger import template
import os

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Veuillez vous connecter pour accéder à cette page.'

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Assurez-vous que le répertoire instance existe
    if not os.path.exists(app.instance_path):
        os.makedirs(app.instance_path)
    
    # Configuration de la base de données
    db_path = os.path.join(app.instance_path, 'agritech.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'dev-key-agritech-pro-2025'
    
    # Configuration du logger
    log_path = os.path.join(app.instance_path, 'app.log')
    app.config['LOG_FILE'] = log_path
    setup_logger(app)

    # Initialisation des extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    from app.models.user import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Enregistrement des blueprints
    from app.routes.auth import auth
    from app.routes.main import main
    from app.api.fields import api_bp
    from app.api.metrics import bp as metrics_bp

    app.register_blueprint(auth)
    app.register_blueprint(main)
    app.register_blueprint(api_bp, url_prefix='/api/v1')
    app.register_blueprint(metrics_bp, url_prefix='/api')

    # Configuration Swagger UI
    SWAGGER_URL = '/api/docs'
    API_URL = '/api/swagger.json'

    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={
            'app_name': "AgriTechPro API"
        }
    )
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

    @app.route("/api/swagger.json")
    def specs():
        return jsonify(template)

    # Création des tables
    with app.app_context():
        db.create_all()

    return app
