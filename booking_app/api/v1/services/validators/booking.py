import datetime
import logging

import pytz
from sqlalchemy import and_

from booking_app.api.v1.defines import (ERROR_MESSAGE, EXIST_LOG_MESSAGE,
                                        NOT_FOUND_MESSAGE, USER_IN_BLOCK_LIST)
from booking_app.db import db
from booking_app.db_models import BlackList as BlackList_db_model
from booking_app.db_models import Booking as Booking_db_model
from booking_app.db_models import Event as Event_db_model


def check_booking_not_exist_or_raise_exception(obj):
    objs = Booking_db_model.query.filter(
        and_(
            Booking_db_model.user_id == obj.user_id,
            Booking_db_model.event_id == obj.event_id,
            Booking_db_model.id != obj.id,
        )
    )
    if objs.count() > 0:
        logging.info(EXIST_LOG_MESSAGE.format(model="booking"))
        raise ValueError("already exist")


def check_event_exist_or_raise_exception(obj_id):
    if db.session.get(Event_db_model, obj_id) is None:
        logging.info(NOT_FOUND_MESSAGE.format(model="event", id=obj_id))
        raise ValueError("event not exist")


def check_event_have_available_tickets_or_raise_exception(obj):
    event = db.session.get(Event_db_model, obj.event_id)
    if event.max_tickets_count <= len(event.bookings):
        logging.info(NOT_FOUND_MESSAGE.format(model="place", id=obj.id))
        raise ValueError("Event have not available tickets")


def check_that_user_is_host_or_owner(obj, user_id):
    if str(obj.user_id) != user_id and str(obj.event.host_id) != user_id:
        raise ValueError("Only host or owner can change/delete object")


def check_that_user_is_not_host(obj):
    event = db.session.get(Event_db_model, obj.event_id)
    if str(obj.user_id) == str(event.host_id):
        raise ValueError("Host can not take ticket for his own event")


def check_that_user_is_owner(obj, user_id):
    if str(obj.user_id) != user_id:
        raise ValueError("Only owner can change/delete object")


def check_event_not_finished_or_raise_exception(obj, api_name):
    event = db.session.get(Event_db_model, obj.event_id)
    event_start = pytz.timezone("UTC").localize(event.event_start)
    if event_start <= datetime.datetime.now(tz=pytz.timezone("UTC")):
        logging.info(
            ERROR_MESSAGE.format(api=api_name, error="Event already finished")
        )
        raise ValueError("Event already finished")


def check_user_not_in_black_list_or_raise_exception(obj):
    event = db.session.get(Event_db_model, obj.event_id)
    if (
        BlackList_db_model.query.filter_by(
            host_id=event.host_id, user_id=obj.user_id
        ).count()
        > 0
    ):
        logging.info(USER_IN_BLOCK_LIST)
        raise ValueError(USER_IN_BLOCK_LIST)
