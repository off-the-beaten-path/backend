from datetime import datetime

from otbp.models import db


class UserModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    created_at = db.Column(db.DateTime,
                           default=datetime.now,
                           nullable=False)

    email = db.Column(db.String(256), nullable=False)
    password = db.Column(db.String(512), nullable=False)
    roles = db.Column(db.String(128), nullable=False)
    is_active = db.Column(db.Boolean, default=True)

    @property
    def rolenames(self):
        try:
            return self.roles.split(',')
        except Exception:
            return []

    @classmethod
    def lookup(cls, email):
        return cls.query.filter_by(email=email).one_or_none()

    @classmethod
    def identify(cls, id):
        return cls.query.get(id)

    @property
    def identity(self):
        return self.id

    def is_valid(self):
        return self.is_active
