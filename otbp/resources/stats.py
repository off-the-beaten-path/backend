from datetime import date, timedelta
from flask_apispec import marshal_with, doc
from flask_apispec.views import MethodResource
from sqlalchemy import func

import flask_praetorian

from otbp.models import CheckInModel, UserModel
from otbp.resources import security_rules
from otbp.schemas import StatsSchema, GlobalStatsSchema


@doc(
    tags=['Stats'],
    security=security_rules
)
class UserStatsResource(MethodResource):

    @marshal_with(StatsSchema, code=200)
    @flask_praetorian.auth_required
    def get(self):
        current_user_id = flask_praetorian.current_user_id()

        num_checkins = CheckInModel.query.filter_by(user_id=current_user_id).count()
        current_streak = 0
        longest_streak = 0

        # Count the current streak by moving backwards day by day until we reach a day with no checkin, or end of list
        today = date.today()
        date_diff = 1

        # if the user does not have a checkin for today, that does not reset current streak
        has_checkins = CheckInModel.query.filter(func.date(CheckInModel.created_at) == today,
                                                 CheckInModel.user_id == current_user_id).count()
        if has_checkins:
            current_streak += 1

        while True:
            target_date = today - timedelta(days=date_diff)
            has_checkins = CheckInModel.query.filter(func.date(CheckInModel.created_at) == target_date,
                                                     CheckInModel.user_id == current_user_id).count() > 0

            if has_checkins:
                current_streak += 1
                date_diff += 1
            else:
                break

        # Count the longest streak by moving backwards day by day until we reach a day with no checkin, and compare
        #  that streak to persisted longest streak

        checkins = CheckInModel.query.filter_by(user_id=current_user_id).order_by(
            CheckInModel.created_at.desc()).all()

        if len(checkins) <= 1:
            longest_streak = len(checkins)
        else:
            possible_streak = 1

            for i in range(len(checkins) - 1):
                prev = checkins[i]
                curr = checkins[i + 1]

                if prev.created_at.date() == curr.created_at.date():
                    # ignore checkins on the same date
                    pass
                elif prev.created_at.date() - timedelta(days=1) == curr.created_at.date():
                    # when checkins are one day apart, increment the longest streak
                    possible_streak += 1
                else:
                    # when checkins are more than one day apart, store and reset the possible longest streak
                    if possible_streak > longest_streak:
                        longest_streak = possible_streak

                    possible_streak = 1

            # Check the last streak
            if possible_streak > longest_streak:
                longest_streak = possible_streak

        resp = {
            'num_checkins': num_checkins,
            'longest_streak': longest_streak,
            'current_streak': current_streak
        }

        return resp, 200


@doc(
    tags=['Stats']
)
class GlobalStatsResource(MethodResource):

    @marshal_with(GlobalStatsSchema, code=200)
    def get(self):

        resp = {
            'num_checkins': CheckInModel.query.count(),
            'num_players': UserModel.query.filter_by(is_active=True).count()
        }

        return resp, 200
