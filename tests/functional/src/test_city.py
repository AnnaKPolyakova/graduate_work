import json
from http import HTTPStatus

from flask import url_for

from booking_app.db import db
from booking_app.db_models import City
from tests.functional.conftest import (
    OBJ_COUNT, TEST_STR_VALUE, TEST_2_STR_VALUE
)
from tests.functional.settings import test_settings


class TestCity:
    def test_cities_get(self, test_client, cities):
        url = url_for("city.cities")
        method = "get"
        status = HTTPStatus.OK
        response = getattr(test_client, method)(url)
        assert response.status_code == status.OK
        assert len(json.loads(response.data.decode("utf-8"))) == min(
            OBJ_COUNT, test_settings.page_size
        )

    def test_city_post(self, test_client, test_db, access_token_headers):
        url = url_for("city.cities")
        method = "post"
        data = {
            "name": TEST_STR_VALUE,
            "timezone": 'Asia/Qatar'
        }
        status = HTTPStatus.CREATED
        before_creation_count = City.query.count()
        response = getattr(test_client, method)(
            url, json=data, headers=access_token_headers
        )
        after_creation_count = City.query.count()
        assert response.status_code == status
        assert before_creation_count + 1 == after_creation_count

    def test_city_delete(self, test_client, access_token_headers, city):
        url = url_for("city.cities_detail", city_id=city.id)
        method = "delete"
        status = HTTPStatus.NO_CONTENT
        before_delete_count = City.query.count()
        response = getattr(test_client, method)(
            url, headers=access_token_headers
        )
        after_delete_count = City.query.count()
        assert response.status_code == status
        assert before_delete_count - 1 == after_delete_count

    def test_city_patch(self, test_client, access_token_headers, city):
        url = url_for("city.cities_detail", city_id=city.id)
        method = "patch"
        data = {
            "name": TEST_2_STR_VALUE,
            "timezone": 'Africa/Windhoek'
        }
        status = HTTPStatus.OK
        response = getattr(test_client, method)(
            url, json=data, headers=access_token_headers
        )
        obj = db.session.get(City, city.id)
        assert response.status_code == status
        assert obj.name == TEST_2_STR_VALUE

    def test_city_get(self, test_client, city):
        url = url_for("city.cities_detail", city_id=city.id)
        method = "get"
        status = HTTPStatus.OK
        response = getattr(test_client, method)(url)
        assert response.status_code == status
