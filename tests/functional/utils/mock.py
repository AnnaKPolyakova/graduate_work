from functools import wraps
from typing import List

from flask import jsonify, request


def mock_authentication_required_decorator(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        headers = request.headers.environ
        if headers.get("HTTP_AUTHORIZATION", None):
            return func(*args, **kwargs)
        return jsonify({"info": "unauthorized access"}), 401

    return wrapped


def mock_superuser_authentication_required_decorator(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        headers = request.headers.environ
        if headers.get("HTTP_AUTHORIZATION", None):
            return func(*args, **kwargs)
        return jsonify({"info": "unauthorized access"}), 401

    return wrapped


def mock_check_film_work_id(request_obj, film_work_id):
    pass


def mock_check_user_exist(request_obj, user_id):
    pass


async def mock_get_users_logins(users_ids: List):
    data = []
    for user_id in users_ids:
        data.append({"id": user_id, "login": "Test"})
    return True, data
