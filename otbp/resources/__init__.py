from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from flask_apispec import FlaskApiSpec
from flask_marshmallow import Marshmallow

ma = Marshmallow()
docs = FlaskApiSpec()

security_rules = [{'auth': []}]


def init_app(app):
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

    from .user import UserRegisterResource, UserLoginResource, UserRefreshResource, UserPasswordResource
    app.add_url_rule('/user/register', view_func=UserRegisterResource.as_view('UserRegisterResource'))
    docs.register(UserRegisterResource, endpoint='UserRegisterResource')

    app.add_url_rule('/user/login', view_func=UserLoginResource.as_view('UserLoginResource'))
    docs.register(UserLoginResource, endpoint='UserLoginResource')

    app.add_url_rule('/user/refresh', view_func=UserRefreshResource.as_view('UserRefreshResource'))
    docs.register(UserRefreshResource, endpoint='UserRefreshResource')

    app.add_url_rule('/user/password', view_func=UserPasswordResource.as_view('UserPasswordResource'))
    docs.register(UserPasswordResource, endpoint='UserPasswordResource')
