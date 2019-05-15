from flask_marshmallow import Marshmallow

import marshmallow

ma = Marshmallow()


def init_app(app):
    # initialize flask-marshmallow
    ma.init_app(app)


# Collect schemas here for universal/simplified imports
from otbp.schemas.user import UserAuthSchema, UserLoginRegisterSchema, UserChangePasswordSchema, UserSchema
from otbp.schemas.error import ErrorSchema
from otbp.schemas.image import ImageSchema
from otbp.schemas.checkin import CheckInSchema, PaginatedCheckInSchema, CheckInListSchema, CheckInResponseSchema
from otbp.schemas.geocache import GeoCacheSchema


class DefaultApiResponseSchema(ma.Schema):
    class Meta:
        strict = True

    message = marshmallow.fields.Str()
