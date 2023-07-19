import random
import uuid

import factory
from booking_app.db_models import City, Place, Event, Booking, BlackList
from booking_app.db_init import db as _db


class CityFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = City
        sqlalchemy_session = _db.session
        exclude = ["city"]

    city = factory.Faker("city", locale="ru_RU")
    id = factory.LazyAttribute(lambda a: uuid.uuid4())
    created_at = factory.Faker("date_time_this_year", before_now=True)
    name = factory.LazyAttribute(
        lambda a: "{}.{}".format(a.city, random.random()/random.random())
    )
    timezone = factory.Faker("timezone")


class PlaceFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Place
        sqlalchemy_session = _db.session
        exclude = ["sentence"]

    sentence = factory.Faker("sentence", locale="ru_RU")
    id = factory.LazyAttribute(lambda a: uuid.uuid4())
    name = factory.LazyAttribute(
        lambda a: "{}.{}".format(a.sentence, random.random())
    )
    city_id = factory.SubFactory(CityFactory)
    created_at = factory.Faker("date_time_this_year", before_now=True)
    address = factory.Faker("address", locale="ru_RU")
    host_id = factory.LazyAttribute(lambda a: uuid.uuid4())


class EventFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Event
        sqlalchemy_session = _db.session

    id = factory.LazyAttribute(lambda a: uuid.uuid4())
    place_id = factory.SubFactory(PlaceFactory)
    created_at = factory.Faker("date_time_this_year", before_now=True)
    host_id = factory.LazyAttribute(lambda a: uuid.uuid4())
    film_work_id = factory.LazyAttribute(lambda a: uuid.uuid4())
    event_start = factory.Faker("date_time_this_year", before_now=True)
    event_end = factory.Faker("date_time_this_year", after_now=True)
    max_tickets_count = random.randint(20, 100)


class BookingFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Booking
        sqlalchemy_session = _db.session

    id = factory.LazyAttribute(lambda a: uuid.uuid4())
    event_id = factory.SubFactory(EventFactory)
    created_at = factory.Faker("date_time_this_year", before_now=True)
    user_id = factory.LazyAttribute(lambda a: uuid.uuid4())


class BlackListFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = BlackList
        sqlalchemy_session = _db.session

    id = factory.LazyAttribute(lambda a: uuid.uuid4())
    created_at = factory.Faker("date_time_this_year", before_now=True)
    user_id = factory.LazyAttribute(lambda a: uuid.uuid4())
    host_id = factory.LazyAttribute(lambda a: uuid.uuid4())
