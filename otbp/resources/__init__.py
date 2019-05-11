from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from flask_apispec import FlaskApiSpec
from flask_marshmallow import Marshmallow

ma = Marshmallow()
docs = FlaskApiSpec()

security_rules = [{'auth': []}]


def init_app(app):
    # initialize flask-marshmallow
    # ma.init_app(app)

    # initialize flask-apispec

    # configure security definitions to support providing a jwt access token in Swagger UI
    security_definitions = {
        'auth': {
            'description': 'Authorization HTTP header with JWT access token, like: Authorization: Bearer asdf.qwer.zxcv',
            'in': 'header',
            'type': 'apiKey',
            'name': 'Authorization'
        }
    }

    app.config.update({
        'APISPEC_SPEC': APISpec(
            title='Off the Beaten Path',
            version='v1',
            plugins=(MarshmallowPlugin(),),
            securityDefinitions=security_definitions,
            openapi_version='2.0'
        ),
        'APISPEC_SWAGGER_UI_URL': '/'
    })

    docs.init_app(app)

