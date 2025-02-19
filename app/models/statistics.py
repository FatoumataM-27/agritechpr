from app import db
from datetime import datetime

class UsageStatistics(db.Model):
    __tablename__ = 'usage_statistics'
    
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    statistics = db.Column(db.JSON, nullable=False)
    
    def __repr__(self):
        return f'<UsageStatistics {self.timestamp}>'
