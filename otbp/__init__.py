from flask import Flask
from flask_cors import CORS


def create_app():
    # create and configure the app
    app = Flask(__name__)
    app.config.from_mapping(
        ERROR_404_HELP=False,
        JWT_ACCESS_LIFESPAN={"hours": 24},
        JWT_REFRESH_LIFESPAN={"days": 30},
        MAIL_DEFAULT_SENDER="noreply@tmk.name",
    )

    # load the instance config
    app.config.from_envvar("OTBP_SETTINGS", silent=False)

    # CORS
    CORS(app)

    from .models import init_app as init_models

    init_models(app)

    from .schemas import init_app as init_schemas

    init_schemas(app)

    from .resources import init_app as init_resources

    init_resources(app)

    from .praetorian import init_praetorian

    init_praetorian(app)

    # app scripts
    from .cli import init_cli

    init_cli(app)

    return app
