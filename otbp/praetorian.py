from flask_praetorian import Praetorian


guard = Praetorian()


def init_praetorian(app):
    from .models.user import UserModel
    guard.init_app(app, UserModel)
