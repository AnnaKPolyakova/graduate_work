import uuid

from sqlalchemy import func
from sqlalchemy.dialects.postgresql import UUID

from booking_app.db import db


class BaseID(db.Model):
    __abstract__ = True

    id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )


class BaseCreate(db.Model):
    __abstract__ = True

    created_at = db.Column(db.DateTime, default=func.now(), nullable=False)


class ToDictMixin:
    def to_dict(self):
        data = self.__dict__
        out = dict()
        for key, value in data.items():
            if key == "_sa_instance_state" or value is None:
                continue
            out[key] = str(value)
        return out


class City(BaseID, BaseCreate, ToDictMixin):
    name = db.Column(db.String(120), unique=True, nullable=False)
    timezone = db.Column(db.String(120), nullable=False)


class Place(BaseID, BaseCreate, ToDictMixin):
    name = db.Column(db.String(120), unique=True, nullable=False)
    city_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("city.id"),
        nullable=False,
    )
    address = db.Column(db.String(120), unique=True, nullable=True)
    host_id = db.Column(UUID(as_uuid=True), nullable=False)
    city = db.relationship(
        "City", backref=db.backref("places"), overlaps="places",
        single_parent=True, cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Place {self.name}>"


class Event(BaseID, BaseCreate, ToDictMixin):
    film_work_id = db.Column(UUID(as_uuid=True), nullable=False)
    place_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("place.id"),
        nullable=False,
    )
    event_start = db.Column(db.DateTime, nullable=False)
    event_end = db.Column(db.DateTime, nullable=False)
    max_tickets_count = db.Column(db.Integer, nullable=False)
    host_id = db.Column(UUID(as_uuid=True), nullable=False)
    place = db.relationship(
        "Place", backref=db.backref("events"), overlaps="events",
        single_parent=True, cascade="all, delete-orphan"
    )


class Booking(BaseID, BaseCreate, ToDictMixin):
    event_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("event.id"),
        nullable=False,
    )
    user_id = db.Column(UUID(as_uuid=True), nullable=False)
    event = db.relationship(
        "Event", backref=db.backref("bookings"), overlaps="bookings",
        single_parent=True, cascade="all, delete-orphan"
    )


class BlackList(BaseID, BaseCreate, ToDictMixin):
    host_id = db.Column(UUID(as_uuid=True), nullable=False)
    user_id = db.Column(UUID(as_uuid=True), nullable=False)
