from app import db
from datetime import datetime

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    due_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='à faire')  # 'à faire' ou 'terminée'
    priority = db.Column(db.String(20), default='moyenne')  # 'basse', 'moyenne', 'haute'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    field_id = db.Column(db.Integer, db.ForeignKey('field.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    notified_overdue = db.Column(db.Boolean, default=False)
    
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

    @staticmethod
    def check_upcoming_tasks():
        """Vérifie les tâches à venir et crée des notifications si nécessaire"""
        from app.models.notification import Notification
        from app import db
        
        # Récupérer toutes les tâches non terminées
        tasks = Task.query.filter_by(status='à faire').all()
        today = datetime.utcnow()
        
        for task in tasks:
            days_remaining = (task.due_date.date() - today.date()).days
            
            # Notification pour les tâches qui arrivent à échéance dans 3 jours
            if days_remaining == 3:
                notification = Notification(
                    title="Tâche à venir",
                    message=f"La tâche '{task.title}' arrive à échéance dans 3 jours",
                    type="warning",
                    user_id=task.user_id
                )
                db.session.add(notification)
            
            # Notification pour les tâches en retard
            elif days_remaining < 0 and not task.notified_overdue:
                notification = Notification(
                    title="Tâche en retard",
                    message=f"La tâche '{task.title}' est en retard de {abs(days_remaining)} jours",
                    type="alert",
                    user_id=task.user_id
                )
                task.notified_overdue = True
                db.session.add(notification)
        
        db.session.commit()
