from datetime import datetime

from otbp.models import db


class GeoCacheModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime,
                           default=datetime.now,
                           nullable=False)
    lat = db.Column(db.Float, nullable=False)
    lng = db.Column(db.Float, nullable=False)

    checkin = db.relationship('CheckInModel')

    user_id = db.Column(db.Integer,
                        db.ForeignKey('user_model.id'),
                        nullable=False)
    user = db.relationship('UserModel')
