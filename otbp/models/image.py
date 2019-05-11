from datetime import datetime

from otbp.models import db


class ImageModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    created_at = db.Column(db.DateTime,
                           default=datetime.utcnow,
                           nullable=False)

    filename = db.Column(db.String(128), nullable=True)
    filepath = db.Column(db.String(512), nullable=True)

    user_id = db.Column(db.Integer,
                        db.ForeignKey('user_model.id'),
                        nullable=False)
    user = db.relationship('UserModel')
