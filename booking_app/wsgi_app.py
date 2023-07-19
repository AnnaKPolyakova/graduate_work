from flask_jwt_extended import JWTManager
from gevent import monkey

monkey.patch_all()

from booking_app.app import create_booking_app

app = create_booking_app()
jwt = JWTManager(app)
