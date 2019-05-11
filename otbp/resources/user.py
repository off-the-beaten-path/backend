from flask_apispec import marshal_with, use_kwargs, doc
from flask_apispec.views import MethodResource
from flask_praetorian.exceptions import AuthenticationError, MissingUserError

import flask_praetorian
import re

from otbp.resources import security_rules
from otbp.models import db, UserModel
from otbp.schemas import (
    UserAuthSchema,
    UserLoginRegisterSchema,
    UserChangePasswordSchema,
    ErrorSchema,
    DefaultApiResponseSchema
)
from otbp.praetorian import guard


@doc(
    tags=['User'],
)
class UserRegisterResource(MethodResource):

    @use_kwargs(UserLoginRegisterSchema)
    @marshal_with(UserAuthSchema, code=201)
    @marshal_with(ErrorSchema, code=400)
    def post(self, email, password):
        # check for existing user
        user = UserModel.query.filter_by(email=email).one_or_none()

        if user is not None:
            return {'message': f'Account for email {email} already exists'}, 400

        # check email
        r = re.compile(r'(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)')
        if not r.match(email):
            return {'message': 'Invalid email address'}, 400

        # check password strength
        if len(password) not in range(10, 32 + 1):
            return {'message': 'Invalid password. Must be between 10 and 32 characters (inclusive)'}, 400

        password = guard.encrypt_password(password)
        user = UserModel(email=email, password=password, roles='player')

        db.session.add(user)
        db.session.commit()

        resp = {
            'jwt': guard.encode_jwt_token(user),
        }

        return resp, 201


@doc(
    tags=['User'],
    security=security_rules
)
class UserPasswordResource(MethodResource):

    @use_kwargs(UserChangePasswordSchema)
    @marshal_with(DefaultApiResponseSchema, code=200)
    @marshal_with(ErrorSchema, code=400)
    @flask_praetorian.auth_required
    def put(self, old, new):
        user = flask_praetorian.current_user()

        if not guard._verify_password(old, user.password):
            return {'message': 'Invalid password'}, 400

        user.password = guard.encrypt_password(new)
        db.session.commit()

        return 'OK', 200


@doc(
    tags=['User'],
)
class UserLoginResource(MethodResource):

    @use_kwargs(UserLoginRegisterSchema)
    @marshal_with(UserAuthSchema, code=200)
    @marshal_with(ErrorSchema, code=400)
    def post(self, email, password):
        try:
            user = guard.authenticate(email, password)
        except (AuthenticationError, MissingUserError) as e:
            return {'message': 'Invalid email or password'}, 400

        resp = {
            'jwt': guard.encode_jwt_token(user),
        }

        return resp, 200


@doc(
    tags=['User'],
    security=security_rules
)
class UserRefreshResource(MethodResource):

    @marshal_with(UserAuthSchema, code=200)
    @marshal_with(ErrorSchema, code=400)
    def get(self):
        """
        Refreshes an existing JWT by creating a new one that is a copy of
        the old except that it has a refreshed access expiration.

        copied from
        https://github.com/dusktreader/flask-praetorian/blob/master/example/refresh.py
        """
        old_token = guard.read_token_from_header()
        new_token = guard.refresh_jwt_token(old_token)

        return {
            'jwt': new_token
        }
