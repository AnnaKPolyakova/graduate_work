from functools import wraps
from http import HTTPStatus

import requests
from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity

from booking_app.settings import settings


def authentication_required(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        headers = request.headers.environ
        authorization = headers.get("HTTP_AUTHORIZATION", None)
        try:
            response = getattr(requests, "get")(
                settings.auth_host,
                headers={
                    "Authorization": authorization,
                },
            )
        except requests.exceptions.ConnectionError:
            return jsonify({"info": "unauthorized access"}), 401
        else:
            if response.status_code != HTTPStatus.OK:
                return jsonify({"info": "unauthorized access"}), 401
        return func(*args, **kwargs)

    return wrapped


def superuser_authentication_required(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        headers = request.headers.environ
        authorization = headers.get("HTTP_AUTHORIZATION", None)
        user_id = get_jwt_identity()
        try:
            response = getattr(requests, "get")(
                settings.auth_host,
                headers={
                    "Authorization": authorization,
                },
            )
        except requests.exceptions.ConnectionError:
            return jsonify({"info": "unauthorized access"}), 401
        else:
            if response.status_code != HTTPStatus.OK:
                return jsonify({"info": "unauthorized access"}), 401
        try:
            response = getattr(requests, "get")(
                settings.get_user_host.format(id=user_id),
                headers={
                    "Authorization": authorization,
                },
            )
        except requests.exceptions.ConnectionError:
            return jsonify({"info": "unauthorized access"}), 401
        else:
            if (
                response.status_code != HTTPStatus.OK
                or response.json().get("is_superuser", False) is False
            ):
                return jsonify({"info": "unauthorized access"}), 401
        return func(*args, **kwargs)

    return wrapped
