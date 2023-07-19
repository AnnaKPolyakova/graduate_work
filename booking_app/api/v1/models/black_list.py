import uuid
from typing import List, Optional

from pydantic import BaseModel, Field, validator

from booking_app.api.v1.models.common import (CreateAtMixin, IDAndConfigMixin,
                                              validate_sorting_value)


class BlackList(IDAndConfigMixin, CreateAtMixin):
    host_id: uuid.UUID
    user_id: uuid.UUID


class BlackListCreate(BaseModel):
    user_id: uuid.UUID


class BlackListFilter(BaseModel):
    host_id: Optional[uuid.UUID]
    user_id: Optional[uuid.UUID]
    sorting: Optional[List[str]] = Field(
        example="&sorting=created_at&sorting=desc"
    )

    @validator("sorting")
    def validate_sorting(cls, value, values, **kwargs):
        validate_sorting_value(value)
