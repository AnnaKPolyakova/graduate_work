from typing import List, Optional

from pydantic import BaseModel, Field, validator

from booking_app.api.v1.models.common import (CreateAtMixin, IDAndConfigMixin,
                                              validate_sorting_value)


class CityFilter(BaseModel):
    city_id: Optional[str]
    sorting: Optional[List[str]] = Field(
        example="&sorting=created_at&sorting=desc",
    )

    @validator("sorting")
    def validate_sorting(cls, value, values, **kwargs):
        validate_sorting_value(value)


class City(IDAndConfigMixin, CreateAtMixin):
    name: str
    timezone: Optional[str]


class CityCreate(BaseModel):
    name: str
    timezone: str


class CityUpdate(BaseModel):
    name: Optional[str]
    timezone: Optional[str]
