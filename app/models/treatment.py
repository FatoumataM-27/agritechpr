from datetime import datetime
from app import db

class Treatment(db.Model):
    """Modèle pour les traitements (pesticides et engrais)"""
    id = db.Column(db.Integer, primary_key=True)
    field_id = db.Column(db.Integer, db.ForeignKey('field.id'), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # pesticide, fertilizer
    product_name = db.Column(db.String(100), nullable=False)
    active_ingredients = db.Column(db.String(200))
    application_date = db.Column(db.DateTime, nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20), nullable=False)
    application_method = db.Column(db.String(100))
    weather_conditions = db.Column(db.String(200))
    waiting_period = db.Column(db.Integer)  # Délai avant récolte en jours
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Relations
    field = db.relationship('Field', backref=db.backref('treatments', lazy=True))
    user = db.relationship('User', backref=db.backref('treatments', lazy=True))

class TreatmentSchedule(db.Model):
    """Modèle pour la planification des traitements"""
    id = db.Column(db.Integer, primary_key=True)
    field_id = db.Column(db.Integer, db.ForeignKey('field.id'), nullable=False)
    treatment_type = db.Column(db.String(50), nullable=False)
    product_name = db.Column(db.String(100), nullable=False)
    planned_date = db.Column(db.DateTime, nullable=False)
    quantity = db.Column(db.Float)
    unit = db.Column(db.String(20))
    notes = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')  # pending, completed, cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Relations
    field = db.relationship('Field', backref=db.backref('treatment_schedules', lazy=True))
    user = db.relationship('User', backref=db.backref('treatment_schedules', lazy=True))
