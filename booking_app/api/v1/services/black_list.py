from booking_app.api.v1.services.base import (ObjCreator, ObjectsGetter,
                                              ObjGetter, ObjRemover)
from booking_app.api.v1.services.validators.black_list import check_user_exist
from booking_app.api.v1.services.validators.common import \
    check_that_user_is_host


class BlackListCreator(ObjCreator):
    def _create_obj(self):
        self.data["host_id"] = self.user_id
        return self.db_model(**self.data)

    def _validate(self):
        try:
            check_user_exist(self.request, self.user_id)
        except ValueError as error:
            return False, str(error)
        return True, ""


class BlackListGetter(ObjGetter):
    def _validate(self):
        if self.user_id is None:
            return False, "can get only host"
        try:
            check_that_user_is_host(self.obj, self.user_id)
        except ValueError as error:
            return False, str(error)
        return True, ""


class BlackListsGetter(ObjectsGetter):
    def _check_filters_obj_if_exist(self):
        host_id = self.query_dict.get("host_id", None)
        if host_id:
            self.filters["host_id"] = host_id
        return True, ""


class BlackListRemover(ObjRemover):
    def _validate(self):
        try:
            check_that_user_is_host(self.obj, self.user_id)
        except ValueError as error:
            return False, str(error)
        return True, ""
