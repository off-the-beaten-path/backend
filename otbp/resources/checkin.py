from flask import current_app
from flask_apispec import marshal_with, doc, use_kwargs
from flask_apispec.views import MethodResource

import flask_praetorian
import marshmallow

from otbp.resources import security_rules
from otbp.models import db, CheckInModel
from otbp.schemas import ErrorSchema, CheckInSchema, PaginatedCheckInSchema


@doc(
    tags=['Check In'],
    security=security_rules
)
class CheckInResource(MethodResource):

    @use_kwargs(CheckInSchema)
    @marshal_with(ErrorSchema, code=401)
    @flask_praetorian.auth_required
    def post(self, text, location, geocache_id, image_id=None):
        checkin = CheckInModel(text=text,
                               lat=location['lat'],
                               lng=location['lng'],
                               final_distance=0.0,
                               geocache_id=geocache_id,
                               image_id=image_id,
                               user_id=flask_praetorian.current_user_id())

        db.session.add(checkin)
        db.session.commit()

        return 'OK', 201


@doc(
    tags=['Check In'],
    security=security_rules
)
class UserCheckInListResource(MethodResource):

    @use_kwargs({
        'page': marshmallow.fields.Int()
    }, locations=['query'])
    @marshal_with(PaginatedCheckInSchema, 200)
    @marshal_with(ErrorSchema, code=401)
    @flask_praetorian.auth_required
    def get(self, user_id, page=0):
        if user_id != flask_praetorian.current_user_id():
            return {'message': 'Unauthorized'}, 401

        checkins = CheckInModel.query \
            .filter_by(user_id=user_id) \
            .order_by(CheckInModel.created_at.desc()) \
            .paginate(page, current_app.config['POSTS_PER_PAGE'], False)

        return checkins, 200
