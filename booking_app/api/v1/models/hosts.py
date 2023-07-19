import uuid
from typing import Optional

from pydantic import BaseModel, Field, validator


class HostFilter(BaseModel):
    city_id: Optional[uuid.UUID]
    sorting: Optional[str] = Field(example="&sorting=desc")

    @validator("sorting")
    def validate_sorting(cls, value, values, **kwargs):
        if value not in ["asc", "desc"]:
            raise ValueError("Sorting invalid, mast be asc or desc")
        return value


class Hosts(BaseModel):
    id: str
    login: str
