from flask_marshmallow import Marshmallow

import marshmallow

ma = Marshmallow()


def init_app(app):
    # initialize flask-marshmallow
    ma.init_app(app)


# Collect schemas here for universal/simplified imports

class DefaultApiResponseSchema(ma.Schema):
    class Meta:
        strict = True

    message = marshmallow.fields.Str()
