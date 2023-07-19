import logging
from datetime import datetime, timezone
from http import HTTPStatus

import pytz
import requests
from sqlalchemy import and_

from booking_app.api.v1.defines import NOT_FOUND_MESSAGE
from booking_app.db import db
from booking_app.db_models import Event as Event_db_model
from booking_app.db_models import Place as Place_db_model
from booking_app.settings import settings


def check_event_date_and_set_to_default_tz(place, new_event):
    data_format = settings.data_format
    event_timezone = pytz.timezone(place.city.timezone)
    try:
        event_start = datetime.strptime(new_event.event_start, data_format)
        event_end = datetime.strptime(new_event.event_end, data_format)
    except Exception:
        raise ValueError(
            "date invalid, use {data_format} format".format(
                data_format=data_format
            )
        )
    event_start_with_tz = event_timezone.localize(event_start)
    event_end_with_tmz = event_timezone.localize(event_end)
    current_time = datetime.now(event_timezone)
    if event_start_with_tz < current_time:
        raise ValueError("event_start has to be in future")
    if event_start_with_tz >= event_end_with_tmz:
        raise ValueError("event_end can not be earlier that event_start")
    if (
        Event_db_model.query.filter(
            and_(
                Event_db_model.place_id == new_event.place_id,
                Event_db_model.event_start >= event_start,
                Event_db_model.event_end <= event_end,
            )
        ).count()
        > 0
        or Event_db_model.query.filter(
            and_(
                Event_db_model.place_id == new_event.place_id,
                Event_db_model.event_start >= event_start,
                Event_db_model.event_start < event_end,
            )
        ).count()
        > 0
        or Event_db_model.query.filter(
            and_(
                Event_db_model.place_id == new_event.place_id,
                Event_db_model.event_end > event_start,
                Event_db_model.event_end <= event_end,
            )
        ).count()
        > 0
    ):
        raise ValueError(
            "Place is already occupied by another event at this time"
        )
    new_event.event_start = event_start_with_tz.astimezone(timezone.utc)
    new_event.event_end = event_end_with_tmz.astimezone(timezone.utc)
    return new_event


def get_place_if_exist_or_raise_exception(obj_id):
    place = db.session.get(Place_db_model, obj_id)
    if place is None:
        logging.info(NOT_FOUND_MESSAGE.format(model="place", id=obj_id))
        raise ValueError("place not exist")
    return place


def check_place_host_is_request_user(obj, user_id):
    if str(obj.host_id) != user_id:
        logging.info(NOT_FOUND_MESSAGE.format(model="place", id=user_id))
        raise ValueError("Only place host can add event")


def check_film_work_id(request, film_work_id):
    headers = request.headers.environ
    authorization = headers.get("HTTP_AUTHORIZATION", None)
    try:
        response = getattr(requests, "get")(
            settings.get_film_host.format(id=film_work_id),
            headers={
                "Authorization": authorization,
            },
        )
    except requests.exceptions.ConnectionError:
        raise ValueError("film_work_id invalid")
    else:
        if response.status_code != HTTPStatus.OK:
            raise ValueError("film_work_id invalid")
