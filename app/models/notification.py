from app import db
from datetime import datetime

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(50), default='info')  # info, warning, alert
    read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'message': self.message,
            'type': self.type,
            'read': self.read,
            'created_at': self.created_at.strftime('%H:%M'),
            'time': self.created_at.strftime('%H:%M')
        }
