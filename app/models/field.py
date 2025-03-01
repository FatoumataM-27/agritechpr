from app import db
from datetime import datetime

class Field(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    size = db.Column(db.Float, nullable=False)  # en hectares
    crop_type = db.Column(db.String(50))
    soil_type = db.Column(db.String(50))
    irrigation_system = db.Column(db.String(50))
    drainage_system = db.Column(db.String(50))
    topography = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relations
    tasks = db.relationship('Task', backref='field', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'size': self.size,
            'crop_type': self.crop_type,
            'soil_type': self.soil_type,
            'irrigation_system': self.irrigation_system,
            'drainage_system': self.drainage_system,
            'topography': self.topography,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
