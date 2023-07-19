from http import HTTPStatus

import requests

from booking_app.settings import settings


def check_user_exist(request, user_id):
    headers = request.headers.environ
    authorization = headers.get("HTTP_AUTHORIZATION", None)
    try:
        response = getattr(requests, "get")(
            settings.get_user_host.format(id=user_id),
            headers={"Authorization": authorization},
        )
    except requests.exceptions.ConnectionError:
        raise ValueError("user_id invalid")
    else:
        if response.status_code != HTTPStatus.OK:
            raise ValueError("user_id invalid")
