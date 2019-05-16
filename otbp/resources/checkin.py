from datetime import date
from flask import current_app
from flask_apispec import marshal_with, doc, use_kwargs
from flask_apispec.views import MethodResource

import flask_praetorian
import marshmallow

from otbp.resources import security_rules
from otbp.models import db, CheckInModel, GeoCacheModel, ImageModel
from otbp.schemas import ErrorSchema, CheckInCreateSchema, CheckInUpdateSchema, PaginatedCheckInSchema, CheckInListSchema, CheckInResponseSchema
from otbp.utils import geodistance


@doc(
    tags=['Check In'],
    security=security_rules
)
class CreateCheckInResource(MethodResource):

    @use_kwargs(CheckInCreateSchema)
    @marshal_with(CheckInResponseSchema, code=201)
    @marshal_with(ErrorSchema, code=400)
    @flask_praetorian.auth_required
    def post(self, location, geocache_id, text=None, image_id=None):
        geocache = GeoCacheModel.query.get(geocache_id)

        if date.today() != geocache.created_at.date():
            return {'message': 'Expired geocache. You cannot check into a geocache after one day.'}, 400

        final_distance = geodistance(location['lat'], location['lng'], geocache.lat, geocache.lng)

        if final_distance > current_app.config['CHECKIN_MIN_DISTANCE']:
            return {'message': 'You are too far away to check in.'}, 400

        checkin = CheckInModel(text=text,
                               lat=location['lat'],
                               lng=location['lng'],
                               final_distance=final_distance,
                               geocache_id=geocache_id,
                               image_id=image_id,
                               user_id=flask_praetorian.current_user_id())

        db.session.add(checkin)
        db.session.commit()

        return checkin, 201


@doc(
    tags=['Check In'],
    security=security_rules
)
class UserCheckInListPaginatedResource(MethodResource):

    @use_kwargs({
        'page': marshmallow.fields.Int()
    }, locations=['query'])
    @marshal_with(PaginatedCheckInSchema, 200)
    @marshal_with(ErrorSchema, code=401)
    @flask_praetorian.auth_required
    def get(self, page=0):
        user_id = flask_praetorian.current_user_id()

        checkins = CheckInModel.query \
            .filter_by(user_id=user_id) \
            .order_by(CheckInModel.created_at.desc()) \
            .paginate(page, current_app.config['POSTS_PER_PAGE'], False)

        return checkins, 200


@doc(
    tags=['Check In'],
    security=security_rules
)
class UserCheckInListResource(MethodResource):

    @marshal_with(CheckInListSchema, 200)
    @marshal_with(ErrorSchema, code=401)
    @flask_praetorian.auth_required
    def get(self):
        user_id = flask_praetorian.current_user_id()

        checkins = CheckInModel.query \
            .filter_by(user_id=user_id) \
            .order_by(CheckInModel.created_at.desc()) \
            .all()

        resp = {
            'items': checkins
        }

        return resp, 200

@doc(
    tags=['Check In'],
    security=security_rules
)
class CheckInResource(MethodResource):

    @marshal_with(CheckInResponseSchema, 200)
    @marshal_with(ErrorSchema, code=401)
    @flask_praetorian.auth_required
    def get(self, checkin_id):
        user_id = flask_praetorian.current_user_id()

        checkin = CheckInModel.query.get(checkin_id)

        if checkin.user_id != user_id:
            return {'message': 'Unauthorized'}, 401

        return checkin, 200

    @use_kwargs(CheckInUpdateSchema)
    @marshal_with(CheckInResponseSchema, code=200)
    @marshal_with(ErrorSchema, code=400)
    @flask_praetorian.auth_required
    def put(self, checkin_id, text=None, image_id=None):
        checkin = CheckInModel.query.get(checkin_id)

        if checkin.user_id != flask_praetorian.current_user_id():
            return {'message': 'Unauthorized'}, 401

        if image_id is not None:
            # Special id to remove the image from the checkin
            if image_id == -1:
                checkin.image_id = None
            else:
                image = ImageModel.query.get(image_id)

                if image is not None:
                    if image.user_id != flask_praetorian.current_user_id():
                        return {'message': 'Unauthorized'}, 401

                    checkin.image_id = image_id

        checkin.text = text

        db.session.commit()

        return checkin, 200
