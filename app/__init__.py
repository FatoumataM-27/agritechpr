from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///agritech.db'
    app.config['SECRET_KEY'] = 'dev-key-agritech-pro-2025'
    app.config['DEBUG'] = True

    db.init_app(app)
    migrate.init_app(app, db)
    
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Veuillez vous connecter pour accéder à cette page.'

    from app.models.user import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from app.routes.auth import auth
    from app.routes.main import main
    from app.api.fields import api_bp

    app.register_blueprint(auth)
    app.register_blueprint(main)
    app.register_blueprint(api_bp, url_prefix='/api/v1')

    with app.app_context():
        db.create_all()

    @app.route('/test')
    def test():
        return 'Le serveur fonctionne correctement!'

    return app
