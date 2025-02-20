from app import db
from datetime import datetime

class MeteoRegion(db.Model):
    """Modèle pour stocker les données météorologiques des régions"""
    __tablename__ = 'meteo_regions'
    
    id = db.Column(db.Integer, primary_key=True)
    region = db.Column(db.String(100), nullable=False, unique=True)
    temperature = db.Column(db.Float, nullable=False)
    humidite = db.Column(db.Integer, nullable=False)
    vent = db.Column(db.Float, nullable=False)
    precipitations = db.Column(db.Float, nullable=False)
    rayonnement = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200))
    icon = db.Column(db.String(10))
    date_mise_a_jour = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        """Convertit l'objet en dictionnaire"""
        return {
            'region': self.region,
            'temperature': round(self.temperature),
            'humidite': self.humidite,
            'vent': round(self.vent),
            'precipitations': round(self.precipitations),
            'rayonnement': round(self.rayonnement),
            'description': self.description,
            'icon': self.icon,
            'date_mise_a_jour': self.date_mise_a_jour.strftime('%Y-%m-%d %H:%M:%S')
        }
