import datetime
import uuid
from typing import List, Optional

import pytz
from pydantic import BaseModel, Field, validator

from booking_app.api.v1.models.common import (CreateAtMixin, IDAndConfigMixin,
                                              validate_sorting_value)
from booking_app.db import db
from booking_app.db_models import Booking as Booking_db_model
from booking_app.db_models import Place as Place_db_model


def get_local_date_str(date, timezone_str):
    timezone = pytz.timezone(timezone_str)
    timezone_utc = pytz.timezone("UTC")
    date_utc = timezone_utc.localize(date)
    localized_datetime = date_utc.astimezone(timezone)
    return str(localized_datetime)


class Event(IDAndConfigMixin, CreateAtMixin):
    film_work_id: uuid.UUID
    place_id: uuid.UUID
    event_start: str
    event_end: str
    max_tickets_count: int
    host_id: uuid.UUID
    number_of_available_tickets: Optional[int]


class EventGet(IDAndConfigMixin, CreateAtMixin):
    film_work_id: uuid.UUID
    place_id: uuid.UUID
    event_start: datetime.datetime
    event_end: datetime.datetime
    max_tickets_count: int
    host_id: uuid.UUID

    def dict(self, *args, **kwargs):
        data = super().dict(*args, **kwargs)
        data["number_of_available_tickets"] = self.number_of_available_tickets
        return data

    @property
    def number_of_available_tickets(cls, **kwargs):
        return (
            cls.max_tickets_count
            - Booking_db_model.query.filter_by(event_id=cls.id).count()
        )

    @validator("event_start")
    def validate_event_start_timezone(cls, value, values, **kwargs):
        timezone_str = db.session.get(
            Place_db_model, values["place_id"]
        ).city.timezone
        return get_local_date_str(value, timezone_str)

    @validator("event_end")
    def validate_event_end_timezone(cls, value, values, **kwargs):
        timezone_str = db.session.get(
            Place_db_model, values["place_id"]
        ).city.timezone
        return get_local_date_str(value, timezone_str)


class EventCreate(BaseModel):
    film_work_id: uuid.UUID
    place_id: uuid.UUID
    event_start: datetime.datetime
    event_end: datetime.datetime
    max_tickets_count: int


class EventUpdate(BaseModel):
    film_work_id: Optional[uuid.UUID]
    place_id: Optional[uuid.UUID]
    event_start: Optional[datetime.datetime]
    event_end: Optional[datetime.datetime]
    max_tickets_count: Optional[int]


class EventFilter(BaseModel):
    place_id: Optional[uuid.UUID]
    host_id: Optional[uuid.UUID]
    earlier_than: Optional[datetime.datetime]
    later_than: Optional[datetime.datetime]
    sorting: Optional[
        List[str]
    ] = Field(example="&sorting=created_at&sorting=desc")

    @validator("sorting")
    def validate_sorting(cls, value, values, **kwargs):
        validate_sorting_value(value)
