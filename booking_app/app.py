from datetime import timedelta
from logging.config import dictConfig

import pytz
from flask import Flask
from flask_jwt_extended import JWTManager
from pydantic import BaseSettings

from booking_app.api.v1.black_list import black_list
from booking_app.api.v1.booking import booking
from booking_app.api.v1.city import city
from booking_app.api.v1.event import event
from booking_app.api.v1.hosts import host
from booking_app.api.v1.place import place
from booking_app.db_init import init_db
from booking_app.init_limiter import init_limiter
from booking_app.logging_settings import logging_settings
from booking_app.settings import settings
from booking_app.utils import booking_doc


def create_booking_app(settings: BaseSettings = settings):
    dictConfig(logging_settings)
    current_app = Flask(__name__)
    init_db(current_app, settings)
    current_app.config["TIMEZONE"] = pytz.timezone(settings.timezone)
    current_app.config["JWT_SECRET_KEY"] = settings.jwt_secret_key
    current_app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
    current_app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)
    current_app.register_blueprint(city, url_prefix="/api/v1/city")
    current_app.register_blueprint(place, url_prefix="/api/v1/place")
    current_app.register_blueprint(event, url_prefix="/api/v1/event")
    current_app.register_blueprint(booking, url_prefix="/api/v1/booking")
    current_app.register_blueprint(host, url_prefix="/api/v1/host")
    current_app.register_blueprint(black_list, url_prefix="/api/v1/black_list")
    booking_doc.register(current_app)
    init_limiter(current_app, settings)
    return current_app


if __name__ == "__main__":
    app = create_booking_app()
    jwt = JWTManager(app)
    app.run(port=8000)
