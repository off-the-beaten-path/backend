import marshmallow

from otbp.schemas import ma


class ImageSchema(ma.Schema):
    class Meta:
        strict = True

    id = marshmallow.fields.Int()
