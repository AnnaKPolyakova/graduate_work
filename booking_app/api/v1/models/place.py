import uuid
from typing import Optional

from pydantic import BaseModel

from booking_app.api.v1.models.common import CreateAtMixin, IDAndConfigMixin


class Place(IDAndConfigMixin, CreateAtMixin):
    name: str
    city_id: uuid.UUID
    address: str
    host_id: uuid.UUID


class PlaceCreate(BaseModel):
    name: str
    city_id: uuid.UUID
    address: str


class PlaceUpdate(BaseModel):
    name: Optional[str]
    city_id: Optional[uuid.UUID]
    address: Optional[str]
