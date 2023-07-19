import logging
from http import HTTPStatus
from typing import List

from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from spectree import Response

from booking_app.api.permissions import authentication_required
from booking_app.api.v1.defines import (END_LOG_MESSAGE, ERROR_MESSAGE,
                                        START_LOG_MESSAGE)
from booking_app.api.v1.models.common import Status
from booking_app.api.v1.models.hosts import HostFilter, Hosts
from booking_app.api.v1.services.hosts import HostsGetter
from booking_app.utils import booking_doc

host = Blueprint("hosts", __name__)


@host.route("/", methods=["GET"])
@booking_doc.validate(
    tags=["host"],
    query=HostFilter,
    resp=Response(
        HTTP_200=(List[Hosts], "Get all event"), HTTP_400=(Status, "Error")
    ),
)
def hosts():
    logging.debug(START_LOG_MESSAGE.format(api="HostAPI", method="get"))
    page = request.args.get("page", default=1, type=int)
    try:
        getter = HostsGetter(query_dict=request.args, page=page)
        result, info = getter.get_objects()
    except Exception as error:
        logging.error(ERROR_MESSAGE.format(api="BookingAPI", error=error))
        return {"status": "false"}, HTTPStatus.BAD_REQUEST
    if result is False:
        return {"status": info}, HTTPStatus.BAD_REQUEST
    logging.debug(END_LOG_MESSAGE.format(api="HostAPI", method="get"))
    return info, HTTPStatus.OK


@host.route("/my/", methods=["GET"])
@jwt_required(verify_type=False)
@authentication_required
@booking_doc.validate(
    tags=["host"],
    query=HostFilter,
    resp=Response(
        HTTP_200=(List[Hosts], "Get all event"), HTTP_400=(Status, "Error")
    ),
)
def my_hosts():
    logging.debug(START_LOG_MESSAGE.format(api="HostAPI", method="delete"))
    user_id = get_jwt_identity()
    page = request.args.get("page", default=1, type=int)
    try:
        getter = HostsGetter(
            query_dict=request.args, page=page, user_id=user_id
        )
        result, info = getter.get_objects()
    except Exception as error:
        logging.error(ERROR_MESSAGE.format(api="BookingAPI", error=error))
        return {"status": "false"}, HTTPStatus.BAD_REQUEST
    if result is False:
        return {"status": info}, HTTPStatus.BAD_REQUEST
    logging.debug(END_LOG_MESSAGE.format(api="HostAPI", method="get"))
    return info, HTTPStatus.OK
