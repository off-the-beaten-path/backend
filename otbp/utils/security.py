from itsdangerous import URLSafeTimedSerializer

ts = URLSafeTimedSerializer('temp')


def init_sec(app):
    ts.secret_key = app.config['SECRET_KEY']
