import marshmallow

from otbp.schemas import ma
from otbp.schemas.user import UserSchema


class LocationSchema(ma.Schema):
    class Meta:
        strict = True

    lat = marshmallow.fields.Float(required=True)
    lng = marshmallow.fields.Float(required=True)


class CheckInSchema(ma.Schema):
    class Meta:
        strict = True

    id = marshmallow.fields.Int(required=False)
    text = marshmallow.fields.Str(required=False)
    location = marshmallow.fields.Nested(LocationSchema, required=True)
    geocache_id = marshmallow.fields.Int(required=True)
    image_id = marshmallow.fields.Int(required=False)

    user = marshmallow.fields.Nested(UserSchema)


class PaginatedCheckInSchema(ma.Schema):
    class Meta:
        strict = True

    items = marshmallow.fields.Nested(CheckInSchema, many=True, required=True)
    page = marshmallow.fields.Int(required=True)
    has_next = marshmallow.fields.Boolean(required=True)
