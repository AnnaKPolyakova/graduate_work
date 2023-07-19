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
from booking_app.api.v1.models.city import CityFilter
from booking_app.api.v1.models.common import Status
from booking_app.api.v1.models.place import Place, PlaceCreate, PlaceUpdate
from booking_app.api.v1.services.place import (PlaceCreator, PlaceGetter,
                                               PlaceRemover, PlacesGetter,
                                               PlaceUpdater)
from booking_app.db_models import Place as Place_db_model
from booking_app.utils import booking_doc

place = Blueprint("place", __name__)


class PlaceAPI(MethodView):
    @booking_doc.validate(
        tags=["place"],
        query=CityFilter,
        resp=Response(
            HTTP_200=(List[Place], "Get all places"),
            HTTP_400=(Status, "Error")
        ),
    )
    def get(self):
        logging.debug(START_LOG_MESSAGE.format(api="PlaceAPI", method="get"))
        page = request.args.get("page", default=1, type=int)
        try:
            getter = PlacesGetter(
                Place_db_model, page=page, query_dict=request.args
            )
            result, info = getter.get_objects()
        except Exception as error:
            logging.error(ERROR_MESSAGE.format(api="PlaceAPI", error=error))
            return {"status": "false"}, HTTPStatus.BAD_REQUEST
        if result is False:
            return {"status": info}, HTTPStatus.BAD_REQUEST
        logging.debug(END_LOG_MESSAGE.format(api="PlaceAPI", method="get"))
        return [
            Place(**plac_obj.to_dict()).dict() for plac_obj in getter.objects
        ], HTTPStatus.OK

    @jwt_required(verify_type=False)
    @authentication_required
    @booking_doc.validate(
        tags=["place"],
        json=PlaceCreate,
        resp=Response(
            HTTP_201=(Place, "Create place"), HTTP_400=(Status, "Error")
        ),
    )
    def post(self):
        logging.debug(START_LOG_MESSAGE.format(api="PlaceAPI", method="post"))
        user_id = get_jwt_identity()
        try:
            creator = PlaceCreator(
                request, Place_db_model, "PlaceAPI", user_id=user_id
            )
            result, info = creator.save()
        except Exception as error:
            logging.error(ERROR_MESSAGE.format(api="PlaceAPI", error=error))
            return {"status": "false"}, HTTPStatus.BAD_REQUEST
        if result is False:
            logging.info(f"PlaceAPI {self.post.__name__} BAD_REQUEST")
            return {"status": info}, HTTPStatus.BAD_REQUEST
        logging.debug(f"PlaceAPI {self.post.__name__} end")
        return Place(**creator.object.to_dict()).dict(), HTTPStatus.CREATED


class PlaceDetailAPI(MethodView):
    @jwt_required(verify_type=False)
    @authentication_required
    @booking_doc.validate(
        tags=["place"],
        json=PlaceUpdate,
        resp=Response(
            HTTP_200=(Place, "Update place"), HTTP_400=(Status, "Error")
        ),
    )
    def patch(self, place_id):
        logging.debug(
            START_LOG_MESSAGE.format(api="PlaceDetailAPI", method="patch")
        )
        user_id = get_jwt_identity()
        new_data = request.get_json()
        try:
            updater = PlaceUpdater(
                new_data,
                Place_db_model,
                place_id,
                "PlaceDetailAPI",
                request,
                user_id=user_id,
            )
            result, info = updater.update()
        except Exception as error:
            logging.error(
                ERROR_MESSAGE.format(api="PlaceDetailAPI", error=error)
            )
            return {"status": "false"}, HTTPStatus.BAD_REQUEST
        if result is False:
            return {"status": info}, HTTPStatus.BAD_REQUEST
        logging.debug(
            END_LOG_MESSAGE.format(api="PlaceDetailAPI", method="patch")
        )
        return Place(**updater.object.to_dict()).dict(), HTTPStatus.OK

    @booking_doc.validate(
        tags=["place"],
        resp=Response(
            HTTP_200=(Place, "Get place"), HTTP_400=(Status, "Error")
        ),
    )
    def get(self, place_id):
        logging.debug(
            START_LOG_MESSAGE.format(api="PlaceDetailAPI", method="get")
        )
        try:
            getter = PlaceGetter(place_id, Place_db_model, "PlaceDetailAPI")
            result, data = getter.get_obj()
        except Exception as error:
            logging.error(ERROR_MESSAGE.format(api="PlaceAPI", error=error))
            return {"status": "false"}, HTTPStatus.BAD_REQUEST
        if result is False:
            return {"status": "not exist"}, HTTPStatus.BAD_REQUEST
        logging.debug(
            END_LOG_MESSAGE.format(api="PlaceDetailAPI", method="get")
        )
        return Place(**getter.object.to_dict()).dict(), HTTPStatus.OK

    @jwt_required(verify_type=False)
    @authentication_required
    @booking_doc.validate(
        tags=["place"],
        resp=Response("HTTP_204", HTTP_400=(Status, "Error")),
    )
    def delete(self, place_id):
        logging.debug(
            START_LOG_MESSAGE.format(api="PlaceDetailAPI", method="delete")
        )
        user_id = get_jwt_identity()
        try:
            remover = PlaceRemover(
                Place_db_model,
                place_id,
                "PlaceDetailAPI",
                ["events"],
                user_id=user_id
            )
            result, info = remover.delete()
        except Exception as error:
            logging.error(
                ERROR_MESSAGE.format(api="PlaceDetailAPI", error=error)
            )
            return {"status": "false"}, HTTPStatus.BAD_REQUEST
        if result is False:
            return {"status": info}, HTTPStatus.BAD_REQUEST
        logging.debug(
            END_LOG_MESSAGE.format(api="PlaceDetailAPI", method="delete")
        )
        return {}, HTTPStatus.NO_CONTENT


place.add_url_rule("/", view_func=PlaceAPI.as_view("places"))
place.add_url_rule(
    "/<path:place_id>/", view_func=PlaceDetailAPI.as_view("places_detail")
)
