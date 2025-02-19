from app import db
from datetime import datetime

class Notification(db.Model):
    """Modèle pour les notifications"""
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(20), default='info')  # info, warning, alert
    read = db.Column(db.Boolean, default=False)
    
    # Clé étrangère vers l'utilisateur
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Métadonnées
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    read_at = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<Notification {self.title}>'
        
    def mark_as_read(self):
        """Marque la notification comme lue"""
        self.read = True
        self.read_at = datetime.utcnow()
        db.session.commit()
