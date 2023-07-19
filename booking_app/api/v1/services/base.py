import logging
import uuid
from typing import List, Optional

from pydantic import BaseModel
from werkzeug.local import LocalProxy

from booking_app.api.v1.defines import ERROR_MESSAGE
from booking_app.api.v1.services.validators.common import (
    check_related_objects_raise_exception_if_exist,
    get_obj_if_exist_or_raise_exception, obj_id_is_uuid_or_raise_exception)
from booking_app.db import db as _db
from booking_app.settings import settings


class ObjCreator:
    def __init__(self, request, db_model, api_name, db=_db, user_id=None):
        self.data: dict = self._get_data(request)
        self.user_id = user_id
        self.db_model: _db.Model = db_model
        self.obj: _db.Model = self._create_obj()
        self.api_name: str = api_name
        self.db: _db = db
        self.request = request

    @staticmethod
    def _get_data(data):
        if type(data) == dict:
            return data
        elif isinstance(data, LocalProxy):
            return data.get_json()

    def _save_obj(self):
        try:
            self.db.session.add(self.obj)
            self.db.session.flush()
            self.db.session.commit()
            self.db.session.refresh(self.obj)
        except Exception as error:
            self.db.session.rollback()
            return False, error
        return True, ""

    def _create_obj(self):
        return self.db_model(**self.data)

    def _validate(self):
        return True, ""

    def save(self):
        result, info = self._validate()
        if result is False:
            return result, info
        return self._save_obj()

    @property
    def object(self):
        if self.obj is None:
            raise ValueError("object not found")
        return self.obj


class ObjRemover:
    def __init__(
        self,
        db_model: BaseModel,
        obj_id: uuid,
        api_name: str,
        related_fields: List = [],
        db=_db,
        user_id=None,
    ):
        self.obj_id = obj_id
        self.db_model: _db.Model = db_model
        self.db: _db = db
        self.obj: Optional[BaseModel] = None
        self.related_fields = related_fields
        self.api_name: str = api_name
        self.user_id = user_id

    def _dell_obj(self):
        try:
            self.db.session.delete(self.obj)
            self.db.session.commit()
        except Exception as error:
            self.db.session.rollback()
            logging.error(ERROR_MESSAGE.format(api=self.api_name, error=error))
            return False, "false"
        return True, ""

    def _common_validate(self):
        try:
            obj_id_is_uuid_or_raise_exception(self.obj_id, self.api_name)
            self.obj = get_obj_if_exist_or_raise_exception(
                self.obj_id, self.db_model, self.db
            )
            check_related_objects_raise_exception_if_exist(
                self.obj, self.related_fields, self.api_name
            )
        except ValueError as error:
            return False, str(error)
        return True, ""

    def _validate(self):
        return True, ""

    def delete(self):
        result, info = self._common_validate()
        if result is False:
            return result, info
        result, info = self._validate()
        if result is False:
            return result, info
        return self._dell_obj()


class ObjUpdater:
    def __init__(
        self,
        new_data,
        db_model,
        obj_id,
        api_name,
        request,
        user_id=None,
        db: _db = _db
    ):
        self.new_data: dict = new_data
        self.db_model = db_model
        self.obj_id = obj_id
        self.obj: Optional[BaseModel] = None
        self.db: _db = db
        self.user_id = user_id
        self.api_name = api_name
        self.request = request

    def _save(self):
        try:
            self.db.session.add(self.obj)
            self.db.session.flush()
            self.db.session.commit()
            self.db.session.refresh(self.obj)
        except Exception as error:
            self.db.session.rollback()
            logging.info(ERROR_MESSAGE.format(error=error))
            return False, error
        return True, ""

    def _update_obj(self):
        for field, value in self.new_data.items():
            setattr(self.obj, field, value)

    def _validate(self):
        return True, ""

    def _get_obj_if_exist(self):
        try:
            obj_id_is_uuid_or_raise_exception(self.obj_id, self.api_name)
            self.obj = get_obj_if_exist_or_raise_exception(
                self.obj_id, self.db_model, self.db
            )
        except ValueError as error:
            return False, str(error)
        return True, ""

    def update(self):
        result, info = self._get_obj_if_exist()
        if result is False:
            return result, info
        self._update_obj()
        result, info = self._validate()
        if result is False:
            return result, info
        return self._save()

    @property
    def object(self):
        if self.obj is None:
            raise ValueError("object not found")
        return self.obj


class ObjGetter:
    def __init__(
        self,
        obj_id,
        db_model,
        api_name,
        db=_db,
        user_id=None,
    ):
        self.db_model: _db.Model = db_model
        self.obj: Optional[BaseModel] = None
        self.db: _db = db
        self.obj_id: str = obj_id
        self.data = dict()
        self.api_name = api_name
        self.user_id = user_id

    def _get_obj_if_exist(self):
        try:
            obj_id_is_uuid_or_raise_exception(self.obj_id, self.api_name)
            self.obj = get_obj_if_exist_or_raise_exception(
                self.obj_id, self.db_model, self.db
            )

        except ValueError as error:
            return False, str(error)
        return True, ""

    def _validate(self):
        return True, ""

    def get_obj(self):
        result, info = self._get_obj_if_exist()
        if result is False:
            return result, info
        result, info = self._validate()
        if result is False:
            return result, info
        return result, info

    @property
    def object(self):
        if self.obj is None:
            raise ValueError("object not found")
        return self.obj


class ObjectsGetter:
    def __init__(
        self,
        db_model,
        page=1,
        db=_db,
        query_dict: dict = dict(),
    ):
        self.db_model: _db.Model = db_model
        self.db: _db = db
        self.page = page
        self.filters = dict()
        self.objs: List = []
        self.query_dict = query_dict
        self.join_filters: dict = dict()
        self.other_filters: List = []
        self.order_by: Optional[List] = query_dict.getlist("sorting", None)

    def _check_filters_obj_if_exist(self):
        return True, ""

    def _get_filtered_obj_with_other_filters(self):
        self.objs = self.objs.filter(*self.other_filters)

    def _sorting(self):
        if self.order_by:
            self.objs = self.objs.order_by(
                getattr(
                    getattr(self.db_model, self.order_by[0]),
                    self.order_by[1]
                )()
            )

    def _check_order_by_field_if_exist(self):
        if self.order_by:
            if self.order_by[0] not in list(self.db_model.__dict__.keys()):
                return False
        return True

    def get_objects(self):
        if not self._check_order_by_field_if_exist():
            return False, "sorting fild invalid"
        result, info = self._check_filters_obj_if_exist()
        if result is False:
            return False, info
        self.objs = self.db_model.query.filter_by(**self.filters)
        if len(self.join_filters) > 0:
            for model, field_and_value in self.join_filters.items():
                self.objs = self.objs.join(model).filter(
                    getattr(model, field_and_value[0]) == field_and_value[1]
                )
        if len(self.other_filters) > 0:
            self._get_filtered_obj_with_other_filters()
        self._sorting()
        self.objs = self.objs.paginate(
            page=self.page, per_page=settings.page_size
        ).items
        return True, ""

    @property
    def objects(self):
        if self.objs is None:
            raise ValueError("object not found")
        return self.objs
