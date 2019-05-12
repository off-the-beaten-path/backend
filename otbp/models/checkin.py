from datetime import datetime

from otbp.models import db


class CheckInModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime,
                           default=datetime.utcnow,
                           nullable=False)

    text = db.Column(db.String(140), nullable=False)

    lat = db.Column(db.Float, nullable=False)
    lng = db.Column(db.Float, nullable=False)
    final_distance = db.Column(db.Float, nullable=False)

    geocache_id = db.Column(db.Integer,
                            db.ForeignKey('geo_cache_model.id'),
                            nullable=False)
    geocache = db.relationship('GeoCacheModel')

    image_id = db.Column(db.Integer,
                         db.ForeignKey('image_model.id'),
                         nullable=True)
    image = db.relationship('ImageModel')

    user_id = db.Column(db.Integer,
                        db.ForeignKey('user_model.id'),
                        nullable=False)
    user = db.relationship('UserModel')
