import json
from http import HTTPStatus

from flask import url_for

from booking_app.db import db
from booking_app.db_models import Booking, Event
from tests.functional.conftest import OBJ_COUNT
from tests.functional.settings import test_settings


class TestBooking:
    def test_bookings_get(self, test_client, bookings):
        url = url_for("booking.bookings")
        method = "get"
        status = HTTPStatus.OK
        response = getattr(test_client, method)(url)
        assert response.status_code == status.OK
        assert len(json.loads(response.data.decode("utf-8"))) == min(
            OBJ_COUNT, test_settings.page_size
        )

    def test_booking_post(
            self,
            test_client,
            test_db,
            event_with_other_host,
            access_token_headers
    ):
        url = url_for("booking.bookings")
        method = "post"
        data = {"event_id": event_with_other_host.id}
        status = HTTPStatus.CREATED
        before_creation_count = Booking.query.count()
        response = getattr(test_client, method)(
            url, json=data, headers=access_token_headers
        )
        after_creation_count = Booking.query.count()
        assert response.status_code == status
        assert before_creation_count + 1 == after_creation_count

    def test_booking_for_user_in_black_list_post(
            self,
            test_client,
            test_db,
            event_with_other_host,
            access_token_headers,
            black_list_with_host_user_2
    ):
        url = url_for("booking.bookings")
        method = "post"
        data = {"event_id": event_with_other_host.id}
        status = HTTPStatus.BAD_REQUEST
        before_creation_count = Booking.query.count()
        response = getattr(test_client, method)(
            url, json=data, headers=access_token_headers
        )
        after_creation_count = Booking.query.count()
        assert response.status_code == status
        assert before_creation_count == after_creation_count

    def test_booking_delete(self, test_client, access_token_headers, booking):
        url = url_for("booking.bookings_detail", booking_id=booking.id)
        method = "delete"
        status = HTTPStatus.NO_CONTENT
        before_delete_count = Booking.query.count()
        response = getattr(test_client, method)(
            url, headers=access_token_headers
        )
        after_delete_count = Booking.query.count()
        assert response.status_code == status
        assert before_delete_count - 1 == after_delete_count

    def test_booking_patch(
            self, test_client,
            access_token_headers,
            booking,
            event_with_other_host
    ):
        """Check that user can change his own booking"""
        url = url_for("booking.bookings_detail", booking_id=booking.id)
        method = "patch"
        data = {"event_id": event_with_other_host.id}
        status = HTTPStatus.OK
        response = getattr(test_client, method)(
            url, json=data, headers=access_token_headers
        )
        obj = db.session.get(Booking, booking.id)
        assert response.status_code == status
        assert obj.event_id == event_with_other_host.id

    def test_booking_patch_with_random_request_user(
            self, test_client,
            random_access_token_headers,
            booking,
            event_with_other_host
    ):
        """Check that user can change not his own booking"""
        url = url_for("booking.bookings_detail", booking_id=booking.id)
        method = "patch"
        data = {"event_id": event_with_other_host.id}
        status = HTTPStatus.BAD_REQUEST
        response = getattr(test_client, method)(
            url, json=data, headers=random_access_token_headers
        )
        assert response.status_code == status

    def test_booking_get(self, test_client, booking):
        url = url_for("booking.bookings_detail", booking_id=booking.id)
        method = "get"
        status = HTTPStatus.OK
        response = getattr(test_client, method)(url)
        assert response.status_code == status

    def test_my_booking_get_with_filter_by_host(
            self,
            test_client,
            user_id,
            user_id_2,
            access_token_headers,
            bookings_with_host_id_user_2_and_other,
            city,
            place
    ):
        url = url_for("booking.my_booking")
        method = "get"
        status = HTTPStatus.OK
        obj_count = db.session.query(Booking).join(Event).filter(
            Booking.user_id == user_id, Event.host_id == user_id_2).count()
        response = getattr(test_client, method)(
            url,
            headers=access_token_headers,
            query_string={"host_id": user_id_2}
        )
        assert response.status_code == status
        assert obj_count == len(
            json.loads(response.data.decode("utf-8"))
        )
