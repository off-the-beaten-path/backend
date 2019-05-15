import marshmallow

from otbp.schemas import ma


class LocationSchema(ma.Schema):
    class Meta:
        strict = True

    lat = marshmallow.fields.Float(required=True)
    lng = marshmallow.fields.Float(required=True)
