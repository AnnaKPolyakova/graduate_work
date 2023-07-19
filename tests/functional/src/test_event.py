import json
import uuid
from datetime import datetime, timedelta
from http import HTTPStatus

from flask import url_for

from booking_app.db import db
from booking_app.db_models import Event
from tests.functional.conftest import OBJ_COUNT, TEST_INT_VALUE
from tests.functional.settings import test_settings


class TestEvent:
    def test_events_get(self, test_client, place, events):
        url = url_for("event.events")
        method = "get"
        status = HTTPStatus.OK
        response = getattr(test_client, method)(url)
        assert response.status_code == status.OK
        assert len(json.loads(response.data.decode("utf-8"))) == min(
            OBJ_COUNT, test_settings.page_size
        )

    def test_event_post(
            self, test_client, test_db, place, access_token_headers
    ):
        url = url_for("event.events")
        method = "post"
        event_start = datetime.now() + timedelta(days=1)
        event_end = datetime.now() + timedelta(days=2)
        data = {
            "film_work_id": uuid.uuid4(),
            "place_id": place.id,
            "event_start": event_start.strftime(test_settings.data_format),
            "event_end": event_end.strftime(test_settings.data_format),
            "max_tickets_count": 5
        }
        status = HTTPStatus.CREATED
        before_creation_count = Event.query.count()
        response = getattr(test_client, method)(
            url, json=data, headers=access_token_headers
        )
        after_creation_count = Event.query.count()
        assert response.status_code == status
        assert before_creation_count + 1 == after_creation_count

    def test_event_delete(self, test_client, access_token_headers, event):
        url = url_for("event.events_detail", event_id=event.id)
        method = "delete"
        status = HTTPStatus.NO_CONTENT
        before_delete_count = Event.query.count()
        response = getattr(test_client, method)(
            url, headers=access_token_headers
        )
        after_delete_count = Event.query.count()
        assert response.status_code == status
        assert before_delete_count - 1 == after_delete_count

    def test_event_patch(self, test_client, access_token_headers, event):
        url = url_for("event.events_detail", event_id=event.id)
        method = "patch"
        data = {"max_tickets_count": TEST_INT_VALUE}
        status = HTTPStatus.OK
        response = getattr(test_client, method)(
            url, json=data, headers=access_token_headers
        )
        obj = db.session.get(Event, event.id)
        assert response.status_code == status
        assert obj.max_tickets_count == TEST_INT_VALUE

    def test_event_get(self, test_client, event):
        url = url_for("event.events_detail", event_id=event.id)
        method = "get"
        status = HTTPStatus.OK
        response = getattr(test_client, method)(url)
        assert response.status_code == status
