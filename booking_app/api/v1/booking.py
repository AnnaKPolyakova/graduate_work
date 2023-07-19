import logging
from http import HTTPStatus
from typing import List

from flask import Blueprint, request
from flask.views import MethodView
from flask_jwt_extended import get_jwt_identity, jwt_required
from spectree import Response

from booking_app.api.permissions import authentication_required
from booking_app.api.v1.defines import (END_LOG_MESSAGE, ERROR_MESSAGE,
                                        START_LOG_MESSAGE)
from booking_app.api.v1.models.booking import (Booking, BookingCreate,
                                               BookingFilter, BookingUpdate,
                                               MyBookingFilter)
from booking_app.api.v1.models.common import Status
from booking_app.api.v1.services.booking import (BookingCreator, BookingGetter,
                                                 BookingRemover,
                                                 BookingsGetter,
                                                 BookingUpdater)
from booking_app.db_models import Booking as Booking_db_model
from booking_app.utils import booking_doc

booking = Blueprint("booking", __name__)


class BookingAPI(MethodView):
    @booking_doc.validate(
        tags=["booking"],
        query=BookingFilter,
        resp=Response(
            HTTP_200=(List[Booking], "Get all booking"),
            HTTP_400=(Status, "Error")
        ),
    )
    def get(self):
        logging.debug(START_LOG_MESSAGE.format(api="BookingAPI", method="get"))
        page = request.args.get("page", default=1, type=int)
        try:
            getter = BookingsGetter(
                Booking_db_model, query_dict=request.args, page=page
            )
            result, info = getter.get_objects()
        except Exception as error:
            logging.error(ERROR_MESSAGE.format(api="BookingAPI", error=error))
            return {"status": "false"}, HTTPStatus.BAD_REQUEST
        if result is False:
            return {"status": info}, HTTPStatus.BAD_REQUEST
        logging.debug(END_LOG_MESSAGE.format(api="BookingAPI", method="get"))
        return [
            Booking(**city_obj.to_dict()).dict() for city_obj in getter.objects
        ], HTTPStatus.OK

    @jwt_required(verify_type=False)
    @authentication_required
    @booking_doc.validate(
        tags=["booking"],
        json=BookingCreate,
        resp=Response(
            HTTP_201=(Booking, "Create booking"), HTTP_400=(Status, "Error")
        ),
    )
    def post(self):
        logging.debug(
            START_LOG_MESSAGE.format(api="BookingAPI", method="post")
        )
        user_id = get_jwt_identity()
        try:
            creator = BookingCreator(
                request, Booking_db_model, "BookingAPI", user_id=user_id
            )
            result, info = creator.save()
        except Exception as error:
            logging.error(ERROR_MESSAGE.format(api="BookingAPI", error=error))
            return {"status": "false"}, HTTPStatus.BAD_REQUEST
        if result is False:
            logging.info(f"BookingAPI {self.post.__name__} BAD_REQUEST")
            return {"status": info}, HTTPStatus.BAD_REQUEST
        logging.debug(f"BookingAPI {self.post.__name__} end")
        return Booking(**creator.object.to_dict()).dict(), HTTPStatus.CREATED


class BookingDetailAPI(MethodView):
    @jwt_required(verify_type=False)
    @authentication_required
    @booking_doc.validate(
        tags=["booking"],
        json=BookingUpdate,
        resp=Response(
            HTTP_200=(Booking, "Update booking"), HTTP_400=(Status, "Error")
        ),
    )
    def patch(self, booking_id):
        logging.debug(
            START_LOG_MESSAGE.format(api="BookingDetailAPI", method="patch")
        )
        user_id = get_jwt_identity()
        new_data = request.get_json()
        try:
            updater = BookingUpdater(
                new_data,
                Booking_db_model,
                booking_id,
                "BookingDetailAPI",
                request,
                user_id,
            )
            result, info = updater.update()
        except Exception as error:
            logging.error(
                ERROR_MESSAGE.format(api="BookingDetailAPI", error=error)
            )
            return {"status": "false"}, HTTPStatus.BAD_REQUEST
        if result is False:
            return {"status": info}, HTTPStatus.BAD_REQUEST
        logging.debug(
            END_LOG_MESSAGE.format(api="BookingDetailAPI", method="patch")
        )
        return Booking(**updater.object.to_dict()).dict()

    @booking_doc.validate(
        tags=["booking"],
        resp=Response(
            HTTP_200=(Booking, "Get booking"), HTTP_400=(Status, "Error")
        ),
    )
    def get(self, booking_id):
        logging.debug(
            START_LOG_MESSAGE.format(api="BookingDetailAPI", method="get")
        )
        try:
            getter = BookingGetter(
                booking_id, Booking_db_model, "BookingDetailAPI"
            )
            result, info = getter.get_obj()
        except Exception as error:
            logging.error(
                ERROR_MESSAGE.format(api="BookingDetailAPI", error=error)
            )
            return {"status": "false"}, HTTPStatus.BAD_REQUEST
        if result is False:
            return {"status": info}, HTTPStatus.BAD_REQUEST
        logging.debug(
            END_LOG_MESSAGE.format(api="BookingDetailAPI", method="get")
        )
        return Booking(**getter.object.to_dict()).dict(), HTTPStatus.OK

    @jwt_required(verify_type=False)
    @authentication_required
    @booking_doc.validate(
        tags=["booking"],
        resp=Response("HTTP_204", HTTP_400=(Status, "Error")),
    )
    def delete(self, booking_id):
        logging.debug(
            START_LOG_MESSAGE.format(api="BookingDetailAPI", method="delete")
        )
        user_id = get_jwt_identity()
        try:
            remover = BookingRemover(
                Booking_db_model,
                booking_id,
                "BookingDetailAPI",
                user_id=user_id
            )
            result, info = remover.delete()
        except Exception as error:
            logging.error(
                ERROR_MESSAGE.format(api="BookingDetailAPI", error=error)
            )
            return {"status": "false"}, HTTPStatus.BAD_REQUEST
        if result is False:
            return {"status": info}, HTTPStatus.BAD_REQUEST
        logging.debug(
            END_LOG_MESSAGE.format(api="BookingDetailAPI", method="get")
        )
        return {}, HTTPStatus.NO_CONTENT


@booking.route("/my/", methods=["GET"])
@jwt_required(verify_type=False)
@authentication_required
@booking_doc.validate(
    tags=["booking"],
    query=MyBookingFilter,
    resp=Response(
        HTTP_200=(List[Booking], "Get my booking"), HTTP_400=(Status, "Error")
    ),
)
def my_booking():
    logging.debug(
        START_LOG_MESSAGE.format(api="BookingDetailAPI", method="get")
    )
    user_id = get_jwt_identity()
    new_args = request.args.copy()
    new_args["user_id"] = user_id
    page = request.args.get("page", default=1, type=int)
    try:
        getter = BookingsGetter(
            Booking_db_model, query_dict=new_args, page=page
        )
        result, info = getter.get_objects()
    except Exception as error:
        logging.error(
            ERROR_MESSAGE.format(api="BookingDetailAPI", error=error)
        )
        return {"status": "false"}, HTTPStatus.BAD_REQUEST
    if result is False:
        return {"status": info}, HTTPStatus.BAD_REQUEST
    logging.debug(END_LOG_MESSAGE.format(api="BookingDetailAPI", method="get"))
    return [
        Booking(**city_obj.to_dict()).dict() for city_obj in getter.objects
    ], HTTPStatus.OK


booking.add_url_rule("/", view_func=BookingAPI.as_view("bookings"))
booking.add_url_rule(
    "/<path:booking_id>/",
    view_func=BookingDetailAPI.as_view("bookings_detail")
)
