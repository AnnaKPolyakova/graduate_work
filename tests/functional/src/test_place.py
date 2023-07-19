import json
from http import HTTPStatus

from flask import url_for

from booking_app.db import db
from booking_app.db_models import Place
from tests.functional.conftest import (
    OBJ_COUNT, TEST_2_STR_VALUE, TEST_STR_VALUE
)
from tests.functional.settings import test_settings


class TestPlace:
    def test_places_get(self, test_client, city, places):
        url = url_for("place.places")
        method = "get"
        status = HTTPStatus.OK
        response = getattr(test_client, method)(url)
        assert response.status_code == status.OK
        assert len(json.loads(response.data.decode("utf-8"))) == min(
            OBJ_COUNT, test_settings.page_size
        )

    def test_place_post(
            self, test_client, test_db, city, access_token_headers
    ):
        url = url_for("place.places")
        method = "post"
        data = {
            "city_id": city.id,
            "name": TEST_STR_VALUE,
            "address": TEST_STR_VALUE
        }
        status = HTTPStatus.CREATED
        before_creation_count = Place.query.count()
        response = getattr(test_client, method)(
            url, json=data, headers=access_token_headers
        )
        after_creation_count = Place.query.count()
        assert response.status_code == status
        assert before_creation_count + 1 == after_creation_count

    def test_place_delete(self, test_client, access_token_headers, place):
        url = url_for("place.places_detail", place_id=place.id)
        method = "delete"
        status = HTTPStatus.NO_CONTENT
        before_delete_count = Place.query.count()
        response = getattr(test_client, method)(
            url, headers=access_token_headers
        )
        after_delete_count = Place.query.count()
        assert response.status_code == status
        assert before_delete_count - 1 == after_delete_count

    def test_place_patch(self, test_client, access_token_headers, place, city):
        url = url_for("place.places_detail", place_id=place.id)
        method = "patch"
        data = {
            "city_id": city.id,
            "name": TEST_2_STR_VALUE,
            "address": TEST_2_STR_VALUE
        }
        status = HTTPStatus.OK
        response = getattr(test_client, method)(
            url, json=data, headers=access_token_headers
        )
        obj = db.session.get(Place, place.id)
        assert response.status_code == status
        assert obj.name == TEST_2_STR_VALUE

    def test_place_get(self, test_client, place):
        url = url_for("place.places_detail", place_id=place.id)
        method = "get"
        status = HTTPStatus.OK
        response = getattr(test_client, method)(url)
        assert response.status_code == status
