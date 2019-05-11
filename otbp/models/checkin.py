from datetime import datetime

from otbp.models import db


class CheckInModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime,
                           default=datetime.utcnow,
                           nullable=False)
    text = db.Column(db.String(140), nullable=False)
    final_distance = db.Column(db.Float, nullable=False)

    location_id = db.Column(db.Integer,
                            db.ForeignKey('geocache.id'),
                            nullable=False)
    location = db.relationship('Geocache')

    image_id = db.Column(db.Integer,
                         db.ForeignKey('image.id'),
                         nullable=True)
    image = db.relationship('Image')

    user_id = db.Column(db.Integer,
                        db.ForeignKey('user.id'),
                        nullable=False)
    user = db.relationship('User')
