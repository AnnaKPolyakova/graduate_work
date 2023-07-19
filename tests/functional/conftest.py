import datetime
import uuid

import pytest
import sqlalchemy
from flask_jwt_extended import (
    create_access_token, JWTManager
)
from sqlalchemy import create_engine, text
from unittest.mock import patch

from booking_app.db_init import db as _db
from booking_app.settings import settings
from tests.functional.settings import test_settings, TestSettings
from tests.functional.utils.factories import (
    CityFactory, PlaceFactory, EventFactory, BookingFactory, BlackListFactory
)
from tests.functional.utils.mock import (
    mock_authentication_required_decorator,
    mock_superuser_authentication_required_decorator, mock_check_film_work_id,
    mock_get_users_logins, mock_check_user_exist
)

OBJ_COUNT = 10

ERROR_INFO = (
    "Проверьте, что при {method} запросе {url} возвращается статус {status}"
)

TEST_STR_VALUE = 'test'
TEST_2_STR_VALUE = 'test2'
TEST_INT_VALUE = 13

patch(
    "booking_app.api.permissions.superuser_authentication_required",
    mock_superuser_authentication_required_decorator
).start()

patch(
    "booking_app.api.permissions.authentication_required",
    mock_authentication_required_decorator,
).start()

patch(
    "booking_app.api.v1.services.utils.get_users_logins",
    mock_get_users_logins,
).start()

patch(
    "booking_app.api.v1.services.validators.event.check_film_work_id",
    mock_check_film_work_id,
).start()
patch(
    "booking_app.api.v1.services.validators.black_list.check_user_exist",
    mock_check_user_exist,
).start()
patch("booking_app.settings.app_settings", return_value=TestSettings())


def get_connect(postgres_db):
    uri_template = "postgresql://{username}:{password}@{host}/{database_name}"
    uri = uri_template.format(
        username=settings.postgres_user,
        password=settings.postgres_password,
        host=settings.postgres_host,
        database_name=postgres_db,
    )
    db = create_engine(uri, isolation_level='AUTOCOMMIT')
    connect = db.connect()
    connect.execution_options(autocommit=False)
    return db, connect


@pytest.fixture(scope='session', autouse=True)
def test_db():
    db, connect = get_connect(settings.postgres_db)
    try:
        connect.execute(
            text(f"CREATE DATABASE {test_settings.postgres_db_test}")
        )
        connect.close()
    except sqlalchemy.exc.ProgrammingError:
        pass
    db, connect = get_connect(test_settings.postgres_db_test)
    yield db
    _db.drop_all()


@pytest.fixture(scope='session', autouse=True)
def test_app(test_db):
    from booking_app.app import create_booking_app
    app = create_booking_app(test_settings)
    app.config['SERVER_NAME'] = "localhost"
    app.config["TESTING"] = True
    yield app


@pytest.fixture(scope='session', autouse=True)
def test_jwt(test_app):
    yield JWTManager(test_app)


@pytest.fixture(scope='session', autouse=True)
def test_client(test_db, test_app):
    with test_app.test_client() as testing_client:
        with test_app.app_context():
            yield testing_client


@pytest.fixture()
def user_id(test_db, test_app):
    return uuid.uuid4()


@pytest.fixture()
def user_id_2(test_db, test_app):
    return uuid.uuid4()


@pytest.fixture()
def user_id_3(test_db, test_app):
    return uuid.uuid4()


@pytest.fixture()
def token_access(test_db, test_app, user_id):
    access_token = create_access_token(identity=user_id)
    return access_token


@pytest.fixture()
def access_token_headers(test_db, test_app, user_id, token_access):
    return {"Authorization": f"Bearer {token_access}"}


@pytest.fixture()
def random_access_token_headers(test_db, test_app):
    access_token = create_access_token(identity=uuid.uuid4())
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture()
def city(test_db, test_app):
    return CityFactory()


@pytest.fixture()
def city_2(test_db, test_app):
    return CityFactory()


@pytest.fixture()
def cities(test_db, test_app):
    return CityFactory.create_batch(OBJ_COUNT)


@pytest.fixture()
def place(test_db, test_app, city, user_id):
    return PlaceFactory(city_id=city.id, host_id=user_id)


@pytest.fixture()
def place_2(test_db, test_app, city, user_id_2):
    return PlaceFactory(city_id=city.id, host_id=user_id_2)


@pytest.fixture()
def places(test_db, test_app, city):
    return PlaceFactory.create_batch(OBJ_COUNT, city_id=city.id)


@pytest.fixture()
def places_with_city_2(test_db, test_app, city_2):
    return PlaceFactory.create_batch(OBJ_COUNT, city_id=city_2.id)


@pytest.fixture()
def event(test_db, test_app, place, user_id):
    return EventFactory(place_id=place.id, host_id=user_id)


@pytest.fixture()
def event_with_other_host(test_db, city, test_app, place_2, user_id_2):
    return EventFactory(
        event_start=datetime.datetime.now() + datetime.timedelta(days=1),
        event_end=datetime.datetime.now() + datetime.timedelta(days=2),
        place_id=place_2.id,
        host_id=user_id_2,
    )


@pytest.fixture()
def events(test_db, test_app, place):
    return EventFactory.create_batch(OBJ_COUNT, place_id=place.id)


@pytest.fixture()
def booking(test_db, test_app, event_with_other_host, user_id):
    return BookingFactory(
        event_id=event_with_other_host.id, user_id=user_id
    )


@pytest.fixture()
def bookings(test_db, test_app, event):
    return BookingFactory.create_batch(OBJ_COUNT, event_id=event.id)


@pytest.fixture()
def bookings_with_host_id_user_2_and_other(
        test_db, test_app, place, city, user_id, user_id_2
):
    user_2_place = PlaceFactory(city_id=city.id, host_id=user_id_2)
    event_objs = EventFactory.create_batch(
        4, place_id=user_2_place.id, host_id=user_id_2
    )
    event_objs += EventFactory.create_batch(4, place_id=place.id)
    booking_objs = []
    for event in event_objs:
        booking_objs.append(BookingFactory(user_id=user_id, event_id=event.id))
    return booking_objs


@pytest.fixture()
def bookings_with_host_id_user_2(
        test_db, test_app, place, city, user_id, user_id_2
):
    user_2_place = PlaceFactory(city_id=city.id, host_id=user_id_2)
    event_objs = EventFactory.create_batch(
        4, place_id=user_2_place.id, host_id=user_id_2
    )
    event_objs += EventFactory.create_batch(
        4, place_id=user_2_place.id, host_id=user_id_2
    )
    booking_objs = []
    for event in event_objs:
        booking_objs.append(BookingFactory(user_id=user_id, event_id=event.id))
    return booking_objs


@pytest.fixture()
def users_bookings_with_different_hosts(
        test_db, test_app, event, user_id, event_with_other_host
):
    return BookingFactory(event_id=event_with_other_host.id, user_id=user_id)


@pytest.fixture()
def black_list_with_host_user(test_db, test_app, user_id, user_id_2):
    return BlackListFactory(host_id=user_id, user_id=user_id_2)


@pytest.fixture()
def black_list_with_host_user_2(test_db, test_app, user_id, user_id_2):
    return BlackListFactory(host_id=user_id_2, user_id=user_id)


@pytest.fixture()
def black_lists(test_db, test_app):
    return BlackListFactory.create_batch(OBJ_COUNT)
