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

    from .user import UserRegisterResource, UserLoginResource, UserRefreshResource, UserPasswordResource, \
        UserDeleteResource, UserExportResource, UserForgotPasswordResource, UserResetPasswordResource, \
        UserVerifyAccountResource

    app.add_url_rule('/user/register', view_func=UserRegisterResource.as_view('UserRegisterResource'))
    docs.register(UserRegisterResource, endpoint='UserRegisterResource')

    app.add_url_rule('/user/login', view_func=UserLoginResource.as_view('UserLoginResource'))
    docs.register(UserLoginResource, endpoint='UserLoginResource')

    app.add_url_rule('/user/refresh', view_func=UserRefreshResource.as_view('UserRefreshResource'))
    docs.register(UserRefreshResource, endpoint='UserRefreshResource')

    app.add_url_rule('/user/password', view_func=UserPasswordResource.as_view('UserPasswordResource'))
    docs.register(UserPasswordResource, endpoint='UserPasswordResource')

    app.add_url_rule('/user/delete', view_func=UserDeleteResource.as_view('UserDeleteResource'))
    docs.register(UserDeleteResource, endpoint='UserDeleteResource')

    app.add_url_rule('/user/export', view_func=UserExportResource.as_view('UserExportResource'))
    docs.register(UserExportResource, endpoint='UserExportResource')

    app.add_url_rule('/user/password/forgot',
                     view_func=UserForgotPasswordResource.as_view('UserForgotPasswordResource'))
    docs.register(UserForgotPasswordResource, endpoint='UserForgotPasswordResource')

    app.add_url_rule('/user/password/reset',
                     view_func=UserResetPasswordResource.as_view('UserResetPasswordResource'))
    docs.register(UserResetPasswordResource, endpoint='UserResetPasswordResource')

    app.add_url_rule('/user/verify',
                     view_func=UserVerifyAccountResource.as_view('UserVerifyAccountResource'))
    docs.register(UserVerifyAccountResource, endpoint='UserVerifyAccountResource')

    from .image import ImageRetrievalResource, ImageUploadResource
    app.add_url_rule('/image/<string:filename>', view_func=ImageRetrievalResource.as_view('ImageRetrievalResource'))
    docs.register(ImageRetrievalResource, endpoint='ImageRetrievalResource')

    app.add_url_rule('/image/', view_func=ImageUploadResource.as_view('ImageUploadResource'))
    docs.register(ImageUploadResource, endpoint='ImageUploadResource')

    from .checkin import CreateCheckInResource, UserCheckInListPaginatedResource, UserCheckInListResource, \
        CheckInResource
    app.add_url_rule('/checkin', view_func=CreateCheckInResource.as_view('CreateCheckInResource'))
    docs.register(CreateCheckInResource, endpoint='CreateCheckInResource')

    app.add_url_rule('/checkin/user/paginated',
                     view_func=UserCheckInListPaginatedResource.as_view('UserCheckInListPaginatedResource'))
    docs.register(UserCheckInListPaginatedResource, endpoint='UserCheckInListPaginatedResource')

    app.add_url_rule('/checkin/user/',
                     view_func=UserCheckInListResource.as_view('UserCheckInListResource'))
    docs.register(UserCheckInListResource, endpoint='UserCheckInListResource')

    app.add_url_rule('/checkin/<int:checkin_id>',
                     view_func=CheckInResource.as_view('CheckInResource'))
    docs.register(CheckInResource, endpoint='CheckInResource')

    from .geocache import GeoCacheLocationResource, CreateGeoCacheResource
    app.add_url_rule('/geocache/active',
                     view_func=GeoCacheLocationResource.as_view('GeoCacheLocationResource'))
    docs.register(GeoCacheLocationResource, endpoint='GeoCacheLocationResource')

    app.add_url_rule('/geocache',
                     view_func=CreateGeoCacheResource.as_view('CreateGeoCacheResource'))
    docs.register(CreateGeoCacheResource, endpoint='CreateGeoCacheResource')

    from .stats import UserStatsResource, GlobalStatsResource
    app.add_url_rule('/stats/',
                     view_func=UserStatsResource.as_view('UserStatsResource'))
    docs.register(UserStatsResource, endpoint='UserStatsResource')

    app.add_url_rule('/stats/global/',
                     view_func=GlobalStatsResource.as_view('GlobalStatsResource'))
    docs.register(GlobalStatsResource, endpoint='GlobalStatsResource')
