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
from booking_app.api.v1.models.common import Status
from booking_app.api.v1.models.event import (Event, EventCreate, EventFilter,
                                             EventGet, EventUpdate)
from booking_app.api.v1.services.event import (EventCreator, EventGetter,
                                               EventRemover, EventsGetter,
                                               EventUpdater)
from booking_app.db_models import Event as Event_db_model
from booking_app.utils import booking_doc

event = Blueprint("event", __name__)


class EventAPI(MethodView):
    @booking_doc.validate(
        tags=["event"],
        query=EventFilter,
        resp=Response(
            HTTP_200=(List[Event], "Get all event"), HTTP_400=(Status, "Error")
        ),
    )
    def get(self):
        logging.debug(START_LOG_MESSAGE.format(api="EventAPI", method="get"))
        page = request.args.get("page", default=1, type=int)
        try:
            getter = EventsGetter(
                Event_db_model, page=page, query_dict=request.args
            )
            result, info = getter.get_objects()
        except Exception as error:
            logging.error(ERROR_MESSAGE.format(api="EventAPI", error=error))
            return {"status": "false"}, HTTPStatus.BAD_REQUEST
        if result is False:
            return {"status": info}, HTTPStatus.BAD_REQUEST
        logging.debug(END_LOG_MESSAGE.format(api="EventAPI", method="get"))
        return [
            EventGet(**city_obj.to_dict()).dict() for
            city_obj in getter.objects
        ], HTTPStatus.OK

    @jwt_required(verify_type=False)
    @authentication_required
    @booking_doc.validate(
        tags=["event"],
        json=EventCreate,
        resp=Response(
            HTTP_201=(Event, "Create event"), HTTP_400=(Status, "Error")
        ),
    )
    def post(self):
        logging.debug(START_LOG_MESSAGE.format(api="EventAPI", method="post"))
        user_id = get_jwt_identity()
        try:
            creator = EventCreator(
                request, Event_db_model, "EventAPI", user_id=user_id
            )
            result, info = creator.save()
        except Exception as error:
            logging.error(ERROR_MESSAGE.format(api="EventAPI", error=error))
            return {"status": "false"}, HTTPStatus.BAD_REQUEST
        if result is False:
            logging.error(ERROR_MESSAGE.format(api="EventAPI", error=info))
            return {"status": info}, HTTPStatus.BAD_REQUEST
        logging.debug(f"EventAPI {self.post.__name__} end")
        return EventGet(**creator.object.to_dict()).dict(), HTTPStatus.CREATED


class EventDetailAPI(MethodView):
    @jwt_required(verify_type=False)
    @authentication_required
    @booking_doc.validate(
        tags=["event"],
        json=EventUpdate,
        resp=Response(
            HTTP_200=(Event, "Update event"), HTTP_400=(Status, "Error")
        ),
    )
    def patch(self, event_id):
        logging.debug(
            START_LOG_MESSAGE.format(api="EventDetailAPI", method="patch")
        )
        user_id = get_jwt_identity()
        new_data = request.get_json()
        try:
            updater = EventUpdater(
                new_data,
                Event_db_model,
                event_id,
                "EventDetailAPI",
                request,
                user_id
            )
            result, info = updater.update()
        except Exception as error:
            logging.error(
                ERROR_MESSAGE.format(api="EventDetailAPI", error=error)
            )
            return {"status": "false"}, HTTPStatus.BAD_REQUEST
        if result is False:
            return {"status": info}, HTTPStatus.BAD_REQUEST
        logging.debug(
            END_LOG_MESSAGE.format(api="EventDetailAPI", method="patch")
        )
        return EventGet(**updater.object.to_dict()).dict()

    @booking_doc.validate(
        tags=["event"],
        resp=Response(
            HTTP_200=(Event, "Get event"), HTTP_400=(Status, "Error")
        ),
    )
    def get(self, event_id):
        logging.debug(
            START_LOG_MESSAGE.format(api="EventDetailAPI", method="get")
        )
        try:
            getter = EventGetter(event_id, Event_db_model, "EventDetailAPI")
            result, info = getter.get_obj()
        except Exception as error:
            logging.error(
                ERROR_MESSAGE.format(api="EventDetailAPI", error=error)
            )
            return {"status": "false"}, HTTPStatus.BAD_REQUEST
        if result is False:
            return {"status": info}, HTTPStatus.BAD_REQUEST
        logging.debug(
            END_LOG_MESSAGE.format(api="EventDetailAPI", method="get")
        )
        return EventGet(**getter.object.to_dict()).dict(), HTTPStatus.OK

    @jwt_required(verify_type=False)
    @authentication_required
    @booking_doc.validate(
        tags=["event"],
        resp=Response("HTTP_204", HTTP_400=(Status, "Error")),
    )
    def delete(self, event_id):
        logging.debug(
            START_LOG_MESSAGE.format(api="EventDetailAPI", method="delete")
        )
        user_id = get_jwt_identity()
        try:
            remover = EventRemover(
                Event_db_model,
                event_id,
                "EventDetailAPI",
                ["bookings"],
                user_id=user_id,
            )
            result, info = remover.delete()
        except Exception as error:
            logging.error(
                ERROR_MESSAGE.format(api="EventDetailAPI", error=error)
            )
            return {"status": "false"}, HTTPStatus.BAD_REQUEST
        if result is False:
            return {"status": info}, HTTPStatus.BAD_REQUEST
        logging.debug(
            END_LOG_MESSAGE.format(api="EventDetailAPI", method="get")
        )
        return {}, HTTPStatus.NO_CONTENT


event.add_url_rule("/", view_func=EventAPI.as_view("events"))
event.add_url_rule(
    "/<path:event_id>/", view_func=EventDetailAPI.as_view("events_detail")
)
