from flask_jwt_extended import JWTManager
from gevent import monkey

monkey.patch_all()

from gevent.pywsgi import WSGIServer

from booking_app.app import create_booking_app

app = create_booking_app()
jwt = JWTManager(app)

if __name__ == "__main__":
    http_server = WSGIServer(("", 8000), app)
    http_server.serve_forever()
