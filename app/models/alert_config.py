from app import db
from datetime import datetime

class AlertConfig(db.Model):
    """Configuration des alertes personnalisables"""
    __tablename__ = 'alert_configs'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    metric = db.Column(db.String(50), nullable=False)  # cpu, memory, disk, etc.
    threshold = db.Column(db.Float, nullable=False)
    comparison = db.Column(db.String(10), nullable=False)  # >, <, >=, <=, ==
    severity = db.Column(db.String(20), nullable=False)  # info, warning, critical
    notification_method = db.Column(db.String(20))  # email, slack, teams
    enabled = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    def __repr__(self):
        return f'<AlertConfig {self.name}>'
    
    def check_condition(self, value):
        """Vérifie si la valeur déclenche l'alerte"""
        if self.comparison == '>':
            return value > self.threshold
        elif self.comparison == '<':
            return value < self.threshold
        elif self.comparison == '>=':
            return value >= self.threshold
        elif self.comparison == '<=':
            return value <= self.threshold
        elif self.comparison == '==':
            return value == self.threshold
        return False
    
    @staticmethod
    def get_active_configs():
        """Récupère toutes les configurations d'alerte actives"""
        return AlertConfig.query.filter_by(enabled=True).all()
    
    @staticmethod
    def get_user_configs(user_id):
        """Récupère les configurations d'alerte d'un utilisateur"""
        return AlertConfig.query.filter_by(user_id=user_id).all()
