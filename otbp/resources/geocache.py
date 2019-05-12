from geopy import Point
from geopy.distance import vincenty
from flask import current_app
from flask_apispec import marshal_with, doc
from flask_apispec.views import MethodResource
from sqlalchemy.sql import func

import flask_praetorian
import random

from otbp.resources import security_rules
from otbp.models import db, GeoCacheModel
from otbp.schemas import ErrorSchema, GeoCacheSchema


@doc(
    tags=['Geocache'],
    security=security_rules
)
class GeoCacheLocationResource(MethodResource):

    @marshal_with(GeoCacheSchema, code=200)
    @marshal_with(ErrorSchema, code=401)
    @flask_praetorian.auth_required
    def get(self, location):
        def geodistance(a_lat, a_lng, b_lat, b_lng):
            return vincenty((a_lat, a_lng), (b_lat, b_lng)).meters

        # location should be in format `lat,lng`
        user_lat, user_lng = tuple(map(float, location.split(',')))

        # attempt to find an existing location
        target_list = GeoCacheModel.query \
            .filter(
            # check for results created today
            func.date(GeoCacheModel.created_at) == func.current_date()
        ) \
            .all()

        # if there are any results
        if len(target_list) > 0:

            # sort the results in ascending order, based on distance from user
            sorted_target_list = sorted(target_list,
                                        key=lambda t: geodistance(user_lat, user_lng, t.lat, t.lng))

            # consider the closest match, test if its distance is acceptable
            candidate = sorted_target_list[0]

            distance = geodistance(
                candidate.lat, candidate.lng,
                user_lat, user_lng
            )

            if distance > current_app.config['TARGET_MIN_DISTANCE'] and \
                    distance < current_app.config['TARGET_MAX_DISTANCE']:
                return candidate, 200

        # naively create a target between MIN to MAX m away from current location
        angle = random.randint(1, 360)
        pdistance = random.randint(current_app.config['TARGET_MIN_DISTANCE'],
                                   current_app.config['TARGET_MAX_DISTANCE'])
        pdistance /= 1000

        target_lat, target_lng, _ = vincenty(kilometers=pdistance) \
            .destination(Point(user_lat, user_lng), angle)

        geocache = GeoCacheModel(lat=target_lat,
                                 lng=target_lng)

        db.session.add(geocache)
        db.session.commit()

        return geocache
