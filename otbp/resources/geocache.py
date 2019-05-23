from flask import current_app
from flask_apispec import marshal_with, doc, use_kwargs
from flask_apispec.views import MethodResource
from geopy import Point
from geopy.distance import vincenty

import flask_praetorian
import random

from otbp.models import db, GeoCacheModel
from otbp.resources import security_rules
from otbp.schemas import ErrorSchema, GeoCacheSchema, LocationSchema


@doc(
    tags=['Geocache'],
    security=security_rules
)
class CreateGeoCacheResource(MethodResource):

    @use_kwargs(LocationSchema)
    @marshal_with(GeoCacheSchema, code=200)
    @marshal_with(ErrorSchema, code=401)
    @flask_praetorian.auth_required
    def post(self, lat, lng):
        # naively create a target between MIN to MAX m away from current location
        angle = random.randint(1, 360)
        pdistance = random.randint(current_app.config['TARGET_MIN_DISTANCE'],
                                   current_app.config['TARGET_MAX_DISTANCE'])
        pdistance /= 1000

        target_lat, target_lng, _ = vincenty(kilometers=pdistance) \
            .destination(Point(lat, lng), angle)

        geocache = GeoCacheModel(lat=target_lat,
                                 lng=target_lng,
                                 user_id=flask_praetorian.current_user_id())

        db.session.add(geocache)
        db.session.commit()

        return geocache


@doc(
    tags=['Geocache'],
    security=security_rules
)
class GeoCacheLocationResource(MethodResource):

    @marshal_with(GeoCacheSchema, code=200)
    @marshal_with(ErrorSchema, code=401)
    @marshal_with(ErrorSchema, code=404)
    @flask_praetorian.auth_required
    def get(self):
        # attempt to find a valid, active geocache
        target = GeoCacheModel.query \
            .filter_by(checkin=None) \
            .filter(GeoCacheModel.user_id == flask_praetorian.current_user_id()) \
            .order_by(GeoCacheModel.created_at.desc()) \
            .first()

        if target is None:
            return {'message': 'No active geocache'}, 404

        return target
