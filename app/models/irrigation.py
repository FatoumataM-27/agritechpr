from datetime import datetime
from app import db

class IrrigationSystem(db.Model):
    """Modèle pour les systèmes d'irrigation"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    field_id = db.Column(db.Integer, db.ForeignKey('field.id'), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # goutte-à-goutte, aspersion, etc.
    capacity = db.Column(db.Float)  # Capacité en litres/heure
    installation_date = db.Column(db.DateTime, nullable=False)
    last_maintenance = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='active')  # active, maintenance, inactive
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relations
    field = db.relationship('Field', backref=db.backref('irrigation_systems', lazy=True))
    schedules = db.relationship('IrrigationSchedule', backref='system', lazy=True)

class IrrigationSchedule(db.Model):
    """Modèle pour les horaires d'irrigation"""
    id = db.Column(db.Integer, primary_key=True)
    system_id = db.Column(db.Integer, db.ForeignKey('irrigation_system.id'), nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    duration = db.Column(db.Integer, nullable=False)  # Durée en minutes
    days = db.Column(db.String(50), nullable=False)  # jours de la semaine (format: "1,2,3,4,5")
    water_amount = db.Column(db.Float)  # Quantité d'eau en litres
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class IrrigationLog(db.Model):
    """Modèle pour les logs d'irrigation"""
    id = db.Column(db.Integer, primary_key=True)
    system_id = db.Column(db.Integer, db.ForeignKey('irrigation_system.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime)
    water_used = db.Column(db.Float)  # Quantité d'eau utilisée en litres
    status = db.Column(db.String(20))  # completed, interrupted, failed
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
