import marshmallow

from otbp.schemas import ma


class GeoCacheSchema(ma.Schema):
    class Meta:
        strict = True

    id = marshmallow.fields.Int()
