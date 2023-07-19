import logging
import uuid

from booking_app.api.v1.defines import ERROR_MESSAGE


def check_obj_uuid(obj_id, api_name):
    try:
        uuid.UUID(obj_id)
    except Exception as error:
        logging.error(ERROR_MESSAGE.format(api=api_name, error=error))
        return False
    else:
        return True


def obj_id_is_uuid_or_raise_exception(obj_id, api_name):
    try:
        uuid.UUID(obj_id)
    except Exception as error:
        logging.error(ERROR_MESSAGE.format(api=api_name, error=error))
        raise ValueError("uuid invalid")


def get_obj_if_exist_or_raise_exception(obj_id, db_model, db):
    obj = db.session.get(db_model, obj_id)
    if obj:
        return obj
    else:
        raise ValueError("object not exist")


def check_related_objects_raise_exception_if_exist(
        obj, related_fields, api_name
):
    for field in related_fields:
        if len(getattr(obj, field)) > 0:
            logging.error(
                ERROR_MESSAGE.format(api=api_name, error="related obj exist")
            )
            raise ValueError("related obj exist")


def check_that_user_is_host(obj, user_id):
    if str(obj.host_id) != user_id:
        raise ValueError("Only host can change/delete object")
