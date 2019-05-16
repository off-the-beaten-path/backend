import marshmallow

from otbp.schemas import ma
from otbp.utils.geohash import encode


class LocationSchema(ma.Schema):
    class Meta:
        strict = True

    lat = marshmallow.fields.Float(required=True)
    lng = marshmallow.fields.Float(required=True)
    geohash = marshmallow.fields.Str(required=False)

    @marshmallow.pre_dump
    def pre_dump(self, loc):
        return {
            'lat': loc['lat'],
            'lng': loc['lng'],
            'geohash': encode(loc['lat'], loc['lng'])
        }
