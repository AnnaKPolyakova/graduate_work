from booking_app.api.v1.services.base import (ObjCreator, ObjectsGetter,
                                              ObjGetter, ObjRemover,
                                              ObjUpdater)
from booking_app.api.v1.services.validators.booking import (
    check_booking_not_exist_or_raise_exception,
    check_event_exist_or_raise_exception,
    check_event_have_available_tickets_or_raise_exception,
    check_event_not_finished_or_raise_exception,
    check_that_user_is_host_or_owner, check_that_user_is_not_host,
    check_that_user_is_owner, check_user_not_in_black_list_or_raise_exception)
from booking_app.db_models import Event as Event_db_model


class BookingCreator(ObjCreator):
    def _create_obj(self):
        self.data["user_id"] = self.user_id
        return self.db_model(**self.data)

    def _validate(self):
        try:
            check_event_exist_or_raise_exception(self.obj.event_id)
            check_event_not_finished_or_raise_exception(
                self.obj, self.api_name
            )
            check_booking_not_exist_or_raise_exception(self.obj)
            check_user_not_in_black_list_or_raise_exception(self.obj)
            check_that_user_is_not_host(self.obj)
            check_event_have_available_tickets_or_raise_exception(self.obj)
        except ValueError as error:
            return False, str(error)
        return True, ""


class BookingUpdater(ObjUpdater):
    def _validate(self):
        try:
            event_id = self.new_data.get("event_id", None)
            if event_id is not None:
                check_event_exist_or_raise_exception(event_id)
                check_booking_not_exist_or_raise_exception(self.obj)
                check_that_user_is_owner(self.obj, self.user_id)
                check_that_user_is_not_host(self.obj)
                check_event_have_available_tickets_or_raise_exception(self.obj)
        except ValueError as error:
            return False, str(error)
        return True, ""


class BookingGetter(ObjGetter):
    pass


class BookingsGetter(ObjectsGetter):
    def _check_filters_obj_if_exist(self):
        event_id = self.query_dict.get("event_id", None)
        if event_id is not None:
            event = self.db.session.get(Event_db_model, event_id)
            if event is None:
                return False, "event not exist"
            else:
                self.filters["event_id"] = event_id
        user_id = self.query_dict.get("user_id", None)
        if user_id:
            self.filters["user_id"] = user_id
        host_id = self.query_dict.get("host_id", None)
        if host_id:
            self.join_filters[Event_db_model] = ["host_id", host_id]
        return True, ""


class BookingRemover(ObjRemover):
    def _validate(self):
        try:
            check_that_user_is_host_or_owner(self.obj, self.user_id)
        except ValueError as error:
            return False, str(error)
        return True, ""
