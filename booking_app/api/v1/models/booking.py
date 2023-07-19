import uuid
from typing import List, Optional

from pydantic import BaseModel, Field, validator

from booking_app.api.v1.models.common import (CreateAtMixin, IDAndConfigMixin,
                                              validate_sorting_value)


class Booking(IDAndConfigMixin, CreateAtMixin):
    event_id: uuid.UUID
    user_id: uuid.UUID


class BookingCreate(BaseModel):
    event_id: uuid.UUID


class BookingUpdate(BaseModel):
    event_id: Optional[uuid.UUID]


class BookingFilter(BaseModel):
    user_id: Optional[uuid.UUID]
    event_id: Optional[uuid.UUID]
    host_id: Optional[uuid.UUID]
    sorting: Optional[List[str]] = Field(
        example="&sorting=created_at&sorting=desc"
    )

    @validator("sorting")
    def validate_sorting(cls, value, values, **kwargs):
        validate_sorting_value(value)


class MyBookingFilter(BaseModel):
    host_id: Optional[uuid.UUID]
    sorting: Optional[List[str]] = Field(
        example="&sorting=created_at&sorting=desc"
    )

    @validator("sorting")
    def validate_sorting(cls, value, values, **kwargs):
        validate_sorting_value(value)
