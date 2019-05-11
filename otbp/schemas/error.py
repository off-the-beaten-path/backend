import marshmallow

from otbp.schemas import ma


class ErrorSchema(ma.Schema):
    class Meta:
        strict = True

    message = marshmallow.fields.Str()
