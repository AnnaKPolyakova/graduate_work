import logging

import pytz
from pytz.exceptions import UnknownTimeZoneError

from booking_app.api.v1.defines import EXIST_LOG_MESSAGE
from booking_app.db_models import City as City_db_model


def check_city_already_exist(obj):
    if (
        City_db_model.query.filter(
            City_db_model.name == obj.name,
            City_db_model.id != obj.id,
        ).count()
        > 0
    ):
        logging.info(EXIST_LOG_MESSAGE.format(model="city"))
        raise ValueError("already exist")


def check_timezone(obj):
    try:
        pytz.timezone(obj.timezone)
    except UnknownTimeZoneError:
        raise ValueError("timezone error")
