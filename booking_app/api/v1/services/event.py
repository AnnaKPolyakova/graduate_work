from booking_app.api.v1.services.base import (
    ObjCreator,
    ObjectsGetter,
    ObjGetter,
    ObjRemover,
    ObjUpdater
)
from booking_app.api.v1.services.utils import change_date_str_to_utc_format
from booking_app.api.v1.services.validators.common import \
    check_that_user_is_host
from booking_app.api.v1.services.validators.event import (
    check_event_date_and_set_to_default_tz, check_film_work_id,
    check_place_host_is_request_user, get_place_if_exist_or_raise_exception)
from booking_app.api.v1.services.validators.place import \
    check_max_tickets_count
from booking_app.db_models import Event as Event_db_model
from booking_app.db_models import Place as Place_db_model


class EventCreator(ObjCreator):
    def _create_obj(self):
        self.data["host_id"] = self.user_id
        return self.db_model(**self.data)

    def _validate(self):
        try:
            check_place_host_is_request_user(self.obj, self.user_id)
            place = get_place_if_exist_or_raise_exception(self.obj.place_id)
            self.obj = check_event_date_and_set_to_default_tz(place, self.obj)
            check_max_tickets_count(self.obj.max_tickets_count, self.api_name)
            check_film_work_id(self.request, self.obj.film_work_id)
        except ValueError as error:
            return False, str(error)
        return True, ""


class EventUpdater(ObjUpdater):
    def _validate(self):
        try:
            check_place_host_is_request_user(self.obj, self.user_id)
            place = get_place_if_exist_or_raise_exception(self.obj.place_id)
            if (
                self.new_data.get("event_start", None) is not None
                or self.new_data.get("event_end", None) is not None
            ):
                self.obj = check_event_date_and_set_to_default_tz(
                    place, self.obj
                )
            if self.new_data.get("max_tickets_count", None) is not None:
                check_max_tickets_count(
                    self.obj.max_tickets_count, self.api_name
                )
            if self.new_data.get("film_work_id", None) is not None:
                check_film_work_id(self.request, self.obj.film_work_id)
        except ValueError as error:
            return False, str(error)
        return True, ""


class EventGetter(ObjGetter):
    pass


class EventsGetter(ObjectsGetter):
    def _check_filters_obj_if_exist(self):
        place_id = self.query_dict.get("place_id", None)
        if place_id is not None:
            place = self.db.session.get(Place_db_model, place_id)
            if place is None:
                return False, "place not exist"
            self.filters["place_id"] = place_id
        host_id = self.query_dict.get("host_id", None)
        if host_id is not None:
            self.filters["host_id"] = host_id
        earlier_than = self.query_dict.get("earlier_than", None)
        later_than = self.query_dict.get("later_than", None)
        if earlier_than:
            self.other_filters.append(
                Event_db_model.event_start <
                change_date_str_to_utc_format(earlier_than)
            )
        if later_than:
            self.other_filters.append(
                Event_db_model.event_start >
                change_date_str_to_utc_format(later_than)
            )
        return True, ""


class EventRemover(ObjRemover):
    def _validate(self):
        try:
            check_that_user_is_host(self.obj, self.user_id)
        except ValueError as error:
            return False, str(error)
        return True, ""
