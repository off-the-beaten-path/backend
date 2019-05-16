from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from flask_apispec import FlaskApiSpec
from flask_marshmallow import Marshmallow

ma = Marshmallow()
docs = FlaskApiSpec()

security_rules = [{'auth': []}]


def init_app(app):
    # initialize flask-marshmallow
    ma.init_app(app)

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

    from .image import ImageRetrievalResource, ImageUploadResource
    app.add_url_rule('/image/<string:filename>', view_func=ImageRetrievalResource.as_view('ImageRetrievalResource'))
    docs.register(ImageRetrievalResource, endpoint='ImageRetrievalResource')

    app.add_url_rule('/image/', view_func=ImageUploadResource.as_view('ImageUploadResource'))
    docs.register(ImageUploadResource, endpoint='ImageUploadResource')

    from .checkin import CheckInResource, UserCheckInListPaginatedResource, UserCheckInListResource, UserCheckInResource
    app.add_url_rule('/checkin/', view_func=CheckInResource.as_view('CheckInResource'))
    docs.register(CheckInResource, endpoint='CheckInResource')

    app.add_url_rule('/checkin/user/paginated',
                     view_func=UserCheckInListPaginatedResource.as_view('UserCheckInListPaginatedResource'))
    docs.register(UserCheckInListPaginatedResource, endpoint='UserCheckInListPaginatedResource')

    app.add_url_rule('/checkin/user/',
                     view_func=UserCheckInListResource.as_view('UserCheckInListResource'))
    docs.register(UserCheckInListResource, endpoint='UserCheckInListResource')

    app.add_url_rule('/checkin/user/<int:checkin_id>',
                     view_func=UserCheckInResource.as_view('UserCheckInResource'))
    docs.register(UserCheckInResource, endpoint='UserCheckInResource')

    from .geocache import GeoCacheLocationResource
    app.add_url_rule('/geocache/<string:location>',
                     view_func=GeoCacheLocationResource.as_view('GeoCacheLocationResource'))
    docs.register(GeoCacheLocationResource, endpoint='GeoCacheLocationResource')
