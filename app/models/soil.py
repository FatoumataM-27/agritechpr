from datetime import datetime
from app import db

class SoilTest(db.Model):
    """Modèle pour les analyses de sol"""
    id = db.Column(db.Integer, primary_key=True)
    field_id = db.Column(db.Integer, db.ForeignKey('field.id'), nullable=False)
    test_date = db.Column(db.DateTime, nullable=False)
    ph_level = db.Column(db.Float)
    nitrogen = db.Column(db.Float)  # en mg/kg
    phosphorus = db.Column(db.Float)  # en mg/kg
    potassium = db.Column(db.Float)  # en mg/kg
    organic_matter = db.Column(db.Float)  # en pourcentage
    moisture = db.Column(db.Float)  # en pourcentage
    texture = db.Column(db.String(50))  # sableux, argileux, limoneux, etc.
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Relations
    field = db.relationship('Field', backref=db.backref('soil_tests', lazy=True))
    user = db.relationship('User', backref=db.backref('soil_tests', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'field_id': self.field_id,
            'test_date': self.test_date.isoformat(),
            'ph_level': self.ph_level,
            'nitrogen': self.nitrogen,
            'phosphorus': self.phosphorus,
            'potassium': self.potassium,
            'organic_matter': self.organic_matter,
            'moisture': self.moisture,
            'texture': self.texture,
            'notes': self.notes
        }

class SoilAmendment(db.Model):
    """Modèle pour les amendements de sol"""
    id = db.Column(db.Integer, primary_key=True)
    field_id = db.Column(db.Integer, db.ForeignKey('field.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    type = db.Column(db.String(50), nullable=False)  # compost, chaux, etc.
    quantity = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20), nullable=False)  # kg, tonnes, etc.
    application_method = db.Column(db.String(100))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Relations
    field = db.relationship('Field', backref=db.backref('soil_amendments', lazy=True))
    user = db.relationship('User', backref=db.backref('soil_amendments', lazy=True))
