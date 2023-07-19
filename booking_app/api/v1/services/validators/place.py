import logging

from booking_app.api.v1.defines import (ERROR_MESSAGE, EXIST_LOG_MESSAGE,
                                        NOT_FOUND_MESSAGE)
from booking_app.db import db
from booking_app.db_models import City as City_db_model
from booking_app.db_models import Place as Place_db_model


def check_place_already_exist(obj):
    if (
        Place_db_model.query.filter(
            Place_db_model.name == obj.name, Place_db_model.id != obj.id
        ).count()
        > 0
    ):
        logging.info(EXIST_LOG_MESSAGE.format(model="place"))
        raise ValueError("already exist")
    if (
        Place_db_model.query.filter(
            Place_db_model.address == obj.address, Place_db_model.id != obj.id
        ).count()
        > 0
    ):
        logging.info(EXIST_LOG_MESSAGE.format(model="place"))
        raise ValueError("already exist")


def check_city_exist(obj_id):
    if db.session.get(City_db_model, obj_id) is None:
        logging.info(NOT_FOUND_MESSAGE.format(model="city", id=obj_id))
        raise ValueError("city not exist")


def check_max_tickets_count(max_tickets_count, api_name):
    if max_tickets_count <= 0:
        logging.info(
            ERROR_MESSAGE.format(
                api=api_name, error="max_tickets_count invalid"
            )
        )
        raise ValueError("max_tickets_count invalid")
