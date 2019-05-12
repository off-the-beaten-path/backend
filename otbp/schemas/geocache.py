import marshmallow

from otbp.schemas import ma
from otbp.schemas.checkin import LocationSchema


class GeoCacheSchema(ma.Schema):
    class Meta:
        strict = True

    id = marshmallow.fields.Int()
    location = marshmallow.fields.Nested(LocationSchema)

    @marshmallow.pre_dump
    def pre_dump(self, geocache):
        return {
            'id': geocache.id,
            'location': {
                'lat': geocache.lat,
                'lng': geocache.lng
            }
        }
