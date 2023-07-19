import json
from http import HTTPStatus

from flask import url_for

from booking_app.db import db
from booking_app.db_models import Place, Event, Booking
from tests.functional.conftest import OBJ_COUNT
from tests.functional.settings import test_settings


class TestHost:
    def test_hosts_get(self, test_client, city, places):
        url = url_for("hosts.hosts")
        method = "get"
        status = HTTPStatus.OK
        response = getattr(test_client, method)(url)
        assert response.status_code == status.OK
        assert len(json.loads(response.data.decode("utf-8"))) == min(
            OBJ_COUNT, test_settings.page_size
        )

    def test_hosts_with_filter_get(
            self, test_client, city, places, places_with_city_2, city_2
    ):
        url = url_for("hosts.hosts")
        method = "get"
        status = HTTPStatus.OK
        response = getattr(
            test_client, method
        )(url, query_string={"city_id": city.id})
        assert response.status_code == status.OK
        assert len(json.loads(response.data.decode("utf-8"))) == min(
            OBJ_COUNT, test_settings.page_size
        )

    def test_my_hosts_get(
        self, test_client, user_id, access_token_headers, place,
            city,
            city_2,
            bookings_with_host_id_user_2
    ):
        url = url_for("hosts.my_hosts")
        method = "get"
        status = HTTPStatus.OK
        response = getattr(
            test_client, method
        )(url, headers=access_token_headers)
        obj_count = len(set(b.event.host_id for b in db.session.query(
            Booking
        ).filter_by(user_id=user_id)))
        assert response.status_code == status.OK
        assert len(json.loads(response.data.decode("utf-8"))) == min(
            obj_count, test_settings.page_size
        )

    def test_my_hosts_with_city_filter_get(
        self, test_client, user_id, access_token_headers, place,
            city,
            city_2,
            bookings_with_host_id_user_2
    ):
        url = url_for("hosts.my_hosts")
        method = "get"
        status = HTTPStatus.OK
        response = getattr(
            test_client, method
        )(url, headers=access_token_headers, query_string={
            "city_id": city_2.id}
          )
        obj_count = len(set(b.event.host_id for b in db.session.query(
            Booking
        ).join(Event).join(Place).filter(
            Booking.user_id == user_id, Place.city_id == city_2.id
        )))
        assert response.status_code == status.OK
        assert len(json.loads(response.data.decode("utf-8"))) == min(
            obj_count, test_settings.page_size
        )
