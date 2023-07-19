import json
import uuid
from http import HTTPStatus

from flask import url_for

from booking_app.db_models import BlackList
from tests.functional.settings import test_settings


class TestBlackList:
    def test_black_lists_get(
            self, test_client, black_lists, access_token_headers
    ):
        url = url_for("black_list.black_lists")
        method = "get"
        status = HTTPStatus.OK
        response = getattr(test_client, method)(
            url, headers=access_token_headers
        )
        obj_count = BlackList.query.count()
        assert response.status_code == status.OK
        assert len(json.loads(response.data.decode("utf-8"))) == min(
            obj_count, test_settings.page_size
        )

    def test_black_lists_post(
            self,
            test_client,
            test_db,
            access_token_headers
    ):
        url = url_for("black_list.black_lists")
        method = "post"
        data = {"user_id": uuid.uuid4()}
        status = HTTPStatus.CREATED
        before_creation_count = BlackList.query.count()
        response = getattr(test_client, method)(
            url, json=data, headers=access_token_headers
        )
        after_creation_count = BlackList.query.count()
        assert response.status_code == status
        assert before_creation_count + 1 == after_creation_count

    def test_black_lists_delete(
            self, test_client, access_token_headers, black_list_with_host_user
    ):
        url = url_for(
            "black_list.black_lists_detail",
            black_list_id=black_list_with_host_user.id
        )
        method = "delete"
        status = HTTPStatus.NO_CONTENT
        before_delete_count = BlackList.query.count()
        response = getattr(test_client, method)(
            url, headers=access_token_headers
        )
        after_delete_count = BlackList.query.count()
        assert response.status_code == status
        assert before_delete_count - 1 == after_delete_count

    def test_black_list_get(
            self, test_client, black_list_with_host_user, access_token_headers
    ):
        url = url_for(
            "black_list.black_lists_detail",
            black_list_id=black_list_with_host_user.id
        )
        method = "get"
        status = HTTPStatus.OK
        response = getattr(test_client, method)(
            url, headers=access_token_headers
        )
        assert response.status_code == status

    def test_my_black_list_get(
            self,
            test_client,
            black_list_with_host_user,
            black_lists,
            user_id,
            access_token_headers
    ):
        url = url_for("black_list.my_black_list")
        method = "get"
        status = HTTPStatus.OK
        obj_count = BlackList.query.filter_by(host_id=user_id).count()
        response = getattr(test_client, method)(
            url,
            headers=access_token_headers,
        )
        assert response.status_code == status
        assert min(obj_count, test_settings.page_size) == len(
            json.loads(response.data.decode("utf-8"))
        )
