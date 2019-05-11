from datetime import datetime

from otbp.models import db


class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime,
                           default=datetime.utcnow,
                           nullable=False)
    filepath = db.Column(db.String(512), nullable=True)