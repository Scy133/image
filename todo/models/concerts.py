import datetime
import uuid
from . import db


class Concert(db.Model):
    __tablename__ = 'concerts'

    id = db.Column(db.String(32), primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    venue = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(10), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Enum('ACTIVE', 'CANCELLED', 'SOLD_OUT'), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "venue": self.venue,
            "date": self.date,
            "capacity": self.capacity,
            "status": self.status
        }

    def __repr__(self):
        return f'<Concert {self.id} {self.name}>'
