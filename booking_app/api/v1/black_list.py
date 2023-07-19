import logging
from http import HTTPStatus
from typing import List

from flask import Blueprint, request
from flask.views import MethodView
from flask_jwt_extended import get_jwt_identity, jwt_required
from spectree import Response

from booking_app.api.permissions import (authentication_required,
                                         superuser_authentication_required)
from booking_app.api.v1.defines import (END_LOG_MESSAGE, ERROR_MESSAGE,
                                        START_LOG_MESSAGE)
from booking_app.api.v1.models.black_list import (BlackList, BlackListCreate,
                                                  BlackListFilter)
from booking_app.api.v1.models.common import Status
from booking_app.api.v1.services.black_list import (BlackListCreator,
                                                    BlackListGetter,
                                                    BlackListRemover,
                                                    BlackListsGetter)
from booking_app.db_models import BlackList as BlackList_db_model
from booking_app.utils import booking_doc

black_list = Blueprint("black_list", __name__)


class BlackListAPI(MethodView):
    @jwt_required(verify_type=False)
    @superuser_authentication_required
    @booking_doc.validate(
        tags=["black list"],
        resp=Response(
            HTTP_200=(List[BlackList], "Get all black lists"),
            HTTP_400=(Status, "Error"),
        ),
        query=BlackListFilter,
    )
    def get(self):
        logging.debug(
            START_LOG_MESSAGE.format(api="BlackListAPI", method="get")
        )
        page = request.args.get("page", default=1, type=int)
        try:
            getter = BlackListsGetter(
                BlackList_db_model, query_dict=request.args, page=page
            )
            result, info = getter.get_objects()
        except Exception as error:
            logging.error(
                ERROR_MESSAGE.format(api="BlackListAPI", error=error)
            )
            return {"status": "false"}, HTTPStatus.BAD_REQUEST
        if result is False:
            return {"status": info}, HTTPStatus.BAD_REQUEST
        logging.debug(END_LOG_MESSAGE.format(api="BlackListAPI", method="get"))
        return [
            BlackList(**obj.to_dict()).dict() for obj in getter.objects
        ], HTTPStatus.OK

    @jwt_required(verify_type=False)
    @authentication_required
    @booking_doc.validate(
        tags=["black list"],
        json=BlackListCreate,
        resp=Response(
            HTTP_201=(BlackList, "Create black list"),
            HTTP_400=(Status, "Error")
        ),
    )
    def post(self):
        logging.debug(
            START_LOG_MESSAGE.format(api="BlackListAPI", method="post")
        )
        user_id = get_jwt_identity()
        try:
            creator = BlackListCreator(
                request, BlackList_db_model, "BlackListAPI", user_id=user_id
            )
            result, info = creator.save()
        except Exception as error:
            logging.error(
                ERROR_MESSAGE.format(api="BlackListAPI", error=error)
            )
            return {"status": "false"}, HTTPStatus.BAD_REQUEST
        if result is False:
            logging.info(f"BlackListAPI {self.post.__name__} BAD_REQUEST")
            return {"status": info}, HTTPStatus.BAD_REQUEST
        logging.debug(f"BlackListAPI {self.post.__name__} end")
        return BlackList(**creator.object.to_dict()).dict(), HTTPStatus.CREATED


class BlackListDetailAPI(MethodView):
    @jwt_required(verify_type=False)
    @authentication_required
    @booking_doc.validate(
        tags=["black list"],
        resp=Response(
            HTTP_200=(BlackList, "Get booking"), HTTP_400=(Status, "Error")
        ),
    )
    def get(self, black_list_id):
        logging.debug(
            START_LOG_MESSAGE.format(api="BlackListDetailAPI", method="get")
        )
        user_id = get_jwt_identity()
        try:
            getter = BlackListGetter(
                black_list_id,
                BlackList_db_model,
                "BlackListDetailAPI",
                user_id=user_id,
            )
            result, info = getter.get_obj()
        except Exception as error:
            logging.error(
                ERROR_MESSAGE.format(api="BlackListDetailAPI", error=error)
            )
            return {"status": "false"}, HTTPStatus.BAD_REQUEST
        if result is False:
            return {"status": info}, HTTPStatus.BAD_REQUEST
        logging.debug(
            END_LOG_MESSAGE.format(api="BlackListDetailAPI", method="get")
        )
        return BlackList(**getter.object.to_dict()).dict(), HTTPStatus.OK

    @jwt_required(verify_type=False)
    @authentication_required
    @booking_doc.validate(
        tags=["black list"],
        resp=Response("HTTP_204", HTTP_400=(Status, "Error")),
    )
    def delete(self, black_list_id):
        logging.debug(
            START_LOG_MESSAGE.format(api="BlackListDetailAPI", method="delete")
        )
        user_id = get_jwt_identity()
        try:
            remover = BlackListRemover(
                BlackList_db_model,
                black_list_id,
                "BlackListDetailAPI",
                user_id=user_id
            )
            result, info = remover.delete()
        except Exception as error:
            logging.error(
                ERROR_MESSAGE.format(api="BlackListDetailAPI", error=error)
            )
            return {"status": "false"}, HTTPStatus.BAD_REQUEST
        if result is False:
            return {"status": info}, HTTPStatus.BAD_REQUEST
        logging.debug(
            END_LOG_MESSAGE.format(api="BlackListDetailAPI", method="delete")
        )
        return {}, HTTPStatus.NO_CONTENT


@black_list.route("/my/", methods=["GET"])
@jwt_required(verify_type=False)
@authentication_required
@booking_doc.validate(
    tags=["black list"],
    resp=Response(
        HTTP_200=(List[BlackList], "Get my black lists"),
        HTTP_400=(Status, "Error")
    ),
)
def my_black_list():
    logging.debug(
        START_LOG_MESSAGE.format(api="BlackListDetailAPI", method="get")
    )
    user_id = get_jwt_identity()
    new_dict = request.args.copy()
    new_dict["host_id"] = user_id
    page = request.args.get("page", default=1, type=int)
    try:
        getter = BlackListsGetter(
            BlackList_db_model,
            query_dict=new_dict,
            page=page,
        )
        result, info = getter.get_objects()
    except Exception as error:
        logging.error(
            ERROR_MESSAGE.format(api="BlackListDetailAPI", error=error)
        )
        return {"status": "false"}, HTTPStatus.BAD_REQUEST
    if result is False:
        return {"status": info}, HTTPStatus.BAD_REQUEST
    logging.debug(
        END_LOG_MESSAGE.format(api="BlackListDetailAPI", method="get")
    )
    return [
        BlackList(**obj.to_dict()).dict() for obj in getter.objects
    ], HTTPStatus.OK


black_list.add_url_rule("/", view_func=BlackListAPI.as_view("black_lists"))
black_list.add_url_rule(
    "/<path:black_list_id>/",
    view_func=BlackListDetailAPI.as_view("black_lists_detail")
)
