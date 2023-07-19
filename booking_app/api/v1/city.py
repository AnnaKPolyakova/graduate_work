import logging
from http import HTTPStatus
from typing import List

from flask import Blueprint, request
from flask.views import MethodView
from flask_jwt_extended import jwt_required
from spectree import Response

from booking_app.api.permissions import (authentication_required,
                                         superuser_authentication_required)
from booking_app.api.v1.defines import (END_LOG_MESSAGE, ERROR_MESSAGE,
                                        START_LOG_MESSAGE)
from booking_app.api.v1.models.city import City, CityCreate, CityUpdate
from booking_app.api.v1.models.common import Status
from booking_app.api.v1.services.city import (CitiesGetter, CityCreator,
                                              CityGetter, CityRemover,
                                              CityUpdater)
from booking_app.db_models import City as City_db_model
from booking_app.utils import booking_doc

city = Blueprint("city", __name__)


class CityAPI(MethodView):
    @booking_doc.validate(
        tags=["city"],
        resp=Response(
            HTTP_200=(List[City], "Get all cities"), HTTP_400=(Status, "Error")
        ),
    )
    def get(self):
        logging.debug(START_LOG_MESSAGE.format(api="CityAPI", method="get"))
        page = request.args.get("page", default=1, type=int)
        logging.debug(1)
        try:
            logging.debug(2)
            getter = CitiesGetter(
                City_db_model, page=page, query_dict=request.args
            )
            logging.debug(3)
            result, info = getter.get_objects()
            logging.debug(4)
        except Exception as error:
            logging.error(ERROR_MESSAGE.format(api="CityAPI", error=error))
            return {"status": "false"}, HTTPStatus.BAD_REQUEST
        if result is False:
            return {"status": info}, HTTPStatus.BAD_REQUEST
        logging.debug(END_LOG_MESSAGE.format(api="CityAPI", method="get"))
        return [
            City(**city_obj.to_dict()).dict() for city_obj in getter.objects
        ], HTTPStatus.OK

    @jwt_required(verify_type=False)
    @superuser_authentication_required
    @booking_doc.validate(
        tags=["city"],
        json=CityCreate,
        resp=Response(
            HTTP_201=(City, "Create city"), HTTP_400=(Status, "Error")
        ),
    )
    def post(self):
        logging.debug(START_LOG_MESSAGE.format(api="CityAPI", method="post"))
        try:
            creator = CityCreator(request, City_db_model, "CityAPI")
            result, info = creator.save()
        except Exception as error:
            logging.error(ERROR_MESSAGE.format(api="CityAPI", error=error))
            return {"status": "false"}, HTTPStatus.BAD_REQUEST
        if result is False:
            logging.info(f"CityAPI {self.post.__name__} BAD_REQUEST")
            return {"status": info}, HTTPStatus.BAD_REQUEST
        logging.debug(f"CityAPI {self.post.__name__} end")
        return City(**creator.object.to_dict()).dict(), HTTPStatus.CREATED


class CityDetailAPI(MethodView):
    @jwt_required(verify_type=False)
    @superuser_authentication_required
    @booking_doc.validate(
        tags=["event"],
        json=CityUpdate,
        resp=Response(
            HTTP_200=(City, "Update city"), HTTP_400=(Status, "Error")
        ),
    )
    def patch(self, city_id):
        logging.debug(
            START_LOG_MESSAGE.format(api="CityDetailAPI", method="patch")
        )
        new_data = request.get_json()
        try:
            updater = CityUpdater(
                new_data, City_db_model, city_id, "CityDetailAPI", request
            )
            result, info = updater.update()
        except Exception as error:
            logging.error(
                ERROR_MESSAGE.format(api="CityDetailAPI", error=error)
            )
            return {"status": "false"}, HTTPStatus.BAD_REQUEST
        if result is False:
            return {"status": info}, HTTPStatus.BAD_REQUEST
        logging.debug(
            END_LOG_MESSAGE.format(api="CityDetailAPI", method="patch")
        )
        return City(**updater.object.to_dict()).dict(), HTTPStatus.OK

    @booking_doc.validate(
        tags=["city"],
        resp=Response(HTTP_200=(City, "Get city"), HTTP_400=(Status, "Error")),
    )
    def get(self, city_id):
        logging.debug(
            START_LOG_MESSAGE.format(api="CityDetailAPI", method="get")
        )
        try:
            getter = CityGetter(city_id, City_db_model, "CityDetailAPI")
            result, info = getter.get_obj()
        except Exception as error:
            logging.error(
                ERROR_MESSAGE.format(api="CityDetailAPI", error=error)
            )
            return {"status": "false"}, HTTPStatus.BAD_REQUEST
        if result is False:
            return {"status": info}, HTTPStatus.BAD_REQUEST
        logging.debug(
            END_LOG_MESSAGE.format(api="CityDetailAPI", method="get")
        )
        return City(**getter.object.to_dict()).dict(), HTTPStatus.OK

    @jwt_required(verify_type=False)
    @authentication_required
    @booking_doc.validate(
        tags=["city"],
        resp=Response("HTTP_204", HTTP_400=(Status, "Error")),
    )
    def delete(self, city_id):
        logging.debug(
            START_LOG_MESSAGE.format(api="CityDetailAPI", method="delete")
        )
        try:
            remover = CityRemover(
                City_db_model,
                city_id,
                "CityDetailAPI",
                ["places"],
            )
            result, info = remover.delete()
        except Exception as error:
            logging.error(
                ERROR_MESSAGE.format(api="CityDetailAPI", error=error)
            )
            return {"status": "false"}, HTTPStatus.BAD_REQUEST
        if result is False:
            return {"status": info}, HTTPStatus.BAD_REQUEST
        logging.debug(
            END_LOG_MESSAGE.format(api="PlaceDetailAPI", method="get")
        )
        return {}, HTTPStatus.NO_CONTENT


city.add_url_rule("/", view_func=CityAPI.as_view("cities"))
city.add_url_rule(
    "/<path:city_id>/", view_func=CityDetailAPI.as_view("cities_detail")
)
