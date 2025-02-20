from datetime import datetime
from app import db

class CropActivity(db.Model):
    """Modèle pour les activités liées aux cultures"""
    id = db.Column(db.Integer, primary_key=True)
    crop_id = db.Column(db.Integer, db.ForeignKey('crop.id'), nullable=False)
    activity_type = db.Column(db.String(50), nullable=False)  # irrigation, fertilization, pesticide, observation
    date = db.Column(db.DateTime, nullable=False)
    quantity = db.Column(db.Float)  # Pour l'irrigation, les engrais, etc.
    unit = db.Column(db.String(20))  # L, kg, etc.
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'crop_id': self.crop_id,
            'activity_type': self.activity_type,
            'date': self.date.isoformat(),
            'quantity': self.quantity,
            'unit': self.unit,
            'notes': self.notes,
            'created_at': self.created_at.isoformat()
        }
