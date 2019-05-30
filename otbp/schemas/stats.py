import marshmallow

from otbp.schemas import ma


class StatsSchema(ma.Schema):
    class Meta:
        strict = True

    num_checkins = marshmallow.fields.Int()
    longest_streak = marshmallow.fields.Int()
    current_streak = marshmallow.fields.Int()
