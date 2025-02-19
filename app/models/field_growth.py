from app import db
from datetime import datetime

class FieldGrowth(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    field_id = db.Column(db.Integer, db.ForeignKey('field.id'), nullable=False)
    growth_score = db.Column(db.Float, nullable=False)  # Score de 0 à 10
    month = db.Column(db.String(20), nullable=False)  # Nom du mois
    year = db.Column(db.Integer, nullable=False)
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'field_id': self.field_id,
            'growth_score': self.growth_score,
            'month': self.month,
            'year': self.year,
            'recorded_at': self.recorded_at.strftime('%Y-%m-%d')
        }
