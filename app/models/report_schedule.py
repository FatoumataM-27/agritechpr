from app import db
from datetime import datetime

class ReportSchedule(db.Model):
    """Configuration des rapports programmés"""
    __tablename__ = 'report_schedules'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    metrics = db.Column(db.Text, nullable=False)  # JSON string of metrics to include
    format = db.Column(db.String(10), nullable=False)  # 'pdf', 'csv', or 'both'
    frequency = db.Column(db.String(20), nullable=False)  # 'daily', 'weekly', 'monthly'
    notification_method = db.Column(db.String(20))  # 'email', 'slack', 'teams'
    slack_channel = db.Column(db.String(100))
    teams_webhook = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True)
    last_run = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @classmethod
    def get_due_schedules(cls):
        """Récupère les rapports qui doivent être générés"""
        now = datetime.utcnow()
        return cls.query.filter(
            cls.is_active == True,
            # Ajouter la logique pour vérifier si le rapport doit être généré
            # selon sa fréquence et sa dernière exécution
        ).all()
    
    def update_last_run(self):
        """Met à jour la date de dernière exécution"""
        self.last_run = datetime.utcnow()
        db.session.commit()
    
    def __repr__(self):
        return f'<ReportSchedule {self.name}>'
