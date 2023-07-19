import asyncio
from typing import List

from booking_app.api.v1.services.utils import (get_paginate_obj_list,
                                               get_users_logins)
from booking_app.db import db as _db
from booking_app.db_models import Booking as Booking_db_model
from booking_app.db_models import City as City_db_model
from booking_app.db_models import Place as Place_db_model


class HostsGetter:
    def __init__(
        self,
        db_model=Place_db_model,
        page=1,
        db=_db,
        query_dict: dict = dict(),
        user_id=None,
    ):
        self.db_model: _db.Model = db_model
        self.db: _db = db
        self.page = page
        self.filters: dict = dict()
        self.objs_ids: List = []
        self.user_id = user_id
        self.query_dict = query_dict
        self.order_by = query_dict.get("sorting", None)

    def _check_filters_obj_if_exist(self):
        city_id = self.query_dict.get("city_id", None)
        if city_id is not None:
            city = self.db.session.get(City_db_model, city_id)
            if city is None:
                return False, "city not exist"
            self.filters["city_id"] = city_id
        return True, ""

    def _host_ids(self):
        places = Place_db_model.query.filter_by(**self.filters)
        if self.user_id:
            users_hots_ids = set(
                str(booking.event.host_id)
                for booking in Booking_db_model.query.filter_by(
                    user_id=self.user_id
                )
            )
            places = places.filter(Place_db_model.host_id.in_(users_hots_ids))
        return [str(place.host_id) for place in places]

    def _sorting(self):
        self.objs_ids.sort()
        if self.order_by == "desc":
            self.objs_ids.reverse()

    def get_objects(self):
        result, info = self._check_filters_obj_if_exist()
        if result is False:
            return False, info
        host_ids = self._host_ids()
        self.objs_ids = get_paginate_obj_list(host_ids, page_numb=self.page)
        self._sorting()
        result, info = asyncio.run(get_users_logins(self.objs_ids))
        if result is False:
            return False, info
        return result, info

    @property
    def objects(self):
        if self.objs_ids is None:
            raise ValueError("object not found")
        return self.objs_ids
