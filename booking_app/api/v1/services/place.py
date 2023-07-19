from booking_app.api.v1.services.base import (ObjCreator, ObjectsGetter,
                                              ObjGetter, ObjRemover,
                                              ObjUpdater)
from booking_app.api.v1.services.validators.common import \
    check_that_user_is_host
from booking_app.api.v1.services.validators.place import (
    check_city_exist, check_place_already_exist)
from booking_app.db_models import City as City_db_model


class PlaceCreator(ObjCreator):
    def _create_obj(self):
        self.data["host_id"] = self.user_id
        return self.db_model(**self.data)

    def _validate(self):
        try:
            check_place_already_exist(self.obj)
            check_city_exist(self.obj.city_id)
        except ValueError as error:
            return False, str(error)
        return True, ""


class PlaceUpdater(ObjUpdater):
    def _validate(self):
        try:
            check_that_user_is_host(self.obj, self.user_id)
            check_place_already_exist(self.obj)
            city_id = self.new_data.get("city_id", None)
            if city_id:
                check_city_exist(city_id)
        except ValueError as error:
            return False, str(error)
        return True, ""


class PlaceGetter(ObjGetter):
    pass


class PlacesGetter(ObjectsGetter):
    def _check_filters_obj_if_exist(self):
        city_id = self.query_dict.get("city_id", None)
        if city_id is None:
            return True, ""
        city = self.db.session.get(City_db_model, city_id)
        if city is None:
            return False, "city not exist"
        self.filters["city_id"] = city_id
        return True, ""


class PlaceRemover(ObjRemover):
    def _validate(self):
        try:
            check_that_user_is_host(self.obj, self.user_id)
        except ValueError as error:
            return False, str(error)
        return True, ""
