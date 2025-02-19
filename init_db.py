from app import create_app, db
from app.models.user import User
from app.models.report_schedule import ReportSchedule
from app.models.alert_config import AlertConfig

app = create_app()

with app.app_context():
    # Création des tables
    db.create_all()
    
    # Création d'un utilisateur admin par défaut
    if not User.query.filter_by(email='admin@agritechpro.com').first():
        admin = User(
            username='admin',
            email='admin@agritechpro.com',
            role='admin'
        )
        admin.set_password('admin123')  # À changer en production !
        db.session.add(admin)
        db.session.commit()
        
    print("Base de données initialisée avec succès !")
