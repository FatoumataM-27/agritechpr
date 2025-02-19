from app import db
from datetime import datetime

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    due_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='à faire')  # 'à faire' ou 'terminée'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    field_id = db.Column(db.Integer, db.ForeignKey('field.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    @property
    def completed(self):
        return self.status == 'terminée'
        
    def days_remaining(self):
        if self.due_date:
            delta = self.due_date - datetime.utcnow()
            return max(0, delta.days)
        return 0
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'due_date': self.due_date.strftime('%Y-%m-%d %H:%M:%S'),
            'status': self.status,
            'completed': self.completed,
            'days_remaining': self.days_remaining(),
            'field_id': self.field_id,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
