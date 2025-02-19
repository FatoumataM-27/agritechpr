from app import db
from datetime import datetime

class WeatherData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    region = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100))
    temperature = db.Column(db.Float, nullable=False)
    humidity = db.Column(db.Float)
    precipitation_probability = db.Column(db.Float)
    wind_speed = db.Column(db.Float)
    solar_radiation = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'region': self.region,
            'city': self.city,
            'temperature': self.temperature,
            'humidity': self.humidity,
            'precipitation_probability': self.precipitation_probability,
            'wind_speed': self.wind_speed,
            'solar_radiation': self.solar_radiation,
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        }
