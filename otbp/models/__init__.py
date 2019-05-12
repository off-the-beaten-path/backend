from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Collect Models here for simplified/universal import statements `from models import XModel, YModel...`
from .user import UserModel
from .image import ImageModel
from .checkin import CheckInModel
from .geocache import GeoCacheModel


def init_app(app):
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
