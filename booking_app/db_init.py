from flask import Flask
from pydantic import BaseSettings

from booking_app.db import db


def init_db(app: Flask, settings: BaseSettings):
    uri_template = "postgresql://{username}:{password}@{host}/{database_name}"
    if settings.test is True:
        db_name = settings.postgres_db_test
    else:
        db_name = settings.postgres_db
    uri = uri_template.format(
        username=settings.postgres_user,
        password=settings.postgres_password,
        host=settings.postgres_host,
        database_name=db_name,
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_DATABASE_URI"] = uri
    db.init_app(app)
    app.app_context().push()
    if settings.debug:
        db.create_all()
    return db


def init_redis():
    pass
