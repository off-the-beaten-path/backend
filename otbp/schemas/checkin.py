import marshmallow

from otbp.schemas import ma
from otbp.schemas.location import LocationSchema
from otbp.schemas.geocache import GeoCacheSchema
from otbp.schemas.image import ImageSchema


class CheckInCreateSchema(ma.Schema):
    class Meta:
        strict = True

    id = marshmallow.fields.Int(required=False)
    text = marshmallow.fields.Str(required=False)
    location = marshmallow.fields.Nested(LocationSchema, required=True)
    geocache_id = marshmallow.fields.Int(required=True)
    image_id = marshmallow.fields.Int(required=False)


class CheckInUpdateSchema(ma.Schema):
    class Meta:
        strict = True

    text = marshmallow.fields.Str(required=False)
    image_id = marshmallow.fields.Int(required=False, allow_none=True)


class CheckInResponseSchema(ma.Schema):
    class Meta:
        strict = True

    id = marshmallow.fields.Int(required=False)
    text = marshmallow.fields.Str(required=False)
    final_distance = marshmallow.fields.Int(required=True)
    location = marshmallow.fields.Nested(LocationSchema, required=True)
    created_at = marshmallow.fields.DateTime(required=True)

    geocache = marshmallow.fields.Nested(GeoCacheSchema, required=True)

    image = marshmallow.fields.Nested(ImageSchema, required=False)

    @marshmallow.pre_dump
    def pre_dump(self, checkin):
        return {
            'id': checkin.id,
            'location': {
                'lat': checkin.lat,
                'lng': checkin.lng
            },
            'text': checkin.text,
            'final_distance': checkin.final_distance,
            'created_at': checkin.created_at,
            'geocache': checkin.geocache,
            'image': checkin.image
        }


class PaginatedCheckInSchema(ma.Schema):
    class Meta:
        strict = True

    items = marshmallow.fields.Nested(CheckInResponseSchema, many=True, required=True)
    page = marshmallow.fields.Int(required=True)
    has_next = marshmallow.fields.Boolean(required=True)


class CheckInListSchema(ma.Schema):
    class Meta:
        strict = True

    items = marshmallow.fields.Nested(CheckInResponseSchema, many=True, required=True)
