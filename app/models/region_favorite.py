from app import db
from datetime import datetime

class RegionFavorite(db.Model):
    """Modèle pour stocker les régions favorites des utilisateurs"""
    __tablename__ = 'region_favorites'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    region = db.Column(db.String(100), nullable=False)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'region': self.region,
            'notes': self.notes,
            'created_at': self.created_at.isoformat()
        }
