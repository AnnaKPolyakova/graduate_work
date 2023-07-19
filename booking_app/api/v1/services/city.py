from booking_app.api.v1.services.base import (ObjCreator, ObjectsGetter,
                                              ObjGetter, ObjRemover,
                                              ObjUpdater)
from booking_app.api.v1.services.validators.city import (
    check_city_already_exist, check_timezone)


class CityCreator(ObjCreator):
    def _validate(self):
        try:
            check_city_already_exist(self.obj)
            check_timezone(self.obj)
        except ValueError as error:
            return False, str(error)
        return True, ""


class CityUpdater(ObjUpdater):
    def _validate(self):
        try:
            if self.new_data.get("timezone", None):
                check_timezone(self.obj)
            name = self.new_data.get("name", None)
            if name and name != self.obj.name:
                check_city_already_exist(self.obj)
        except ValueError as error:
            return False, str(error)
        return True, ""


class CityRemover(ObjRemover):
    pass


class CityGetter(ObjGetter):
    pass


class CitiesGetter(ObjectsGetter):
    pass
