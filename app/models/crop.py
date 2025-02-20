from datetime import datetime
from app import db

class Crop(db.Model):
    """Modèle pour les cultures"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    variety = db.Column(db.String(100))
    planting_date = db.Column(db.DateTime, nullable=False)
    expected_harvest_date = db.Column(db.DateTime)
    field_id = db.Column(db.Integer, db.ForeignKey('field.id'), nullable=False)
    status = db.Column(db.String(20), default='active')  # active, harvested, failed
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relations
    user = db.relationship('User', backref=db.backref('crops', lazy=True))
    field = db.relationship('Field', backref=db.backref('crops', lazy=True))
    activities = db.relationship('CropActivity', backref='crop', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'variety': self.variety,
            'planting_date': self.planting_date.isoformat() if self.planting_date else None,
            'expected_harvest_date': self.expected_harvest_date.isoformat() if self.expected_harvest_date else None,
            'field_id': self.field_id,
            'status': self.status,
            'notes': self.notes
        }
