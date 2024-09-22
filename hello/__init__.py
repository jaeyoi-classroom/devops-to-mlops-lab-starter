from flask import Flask

from . import api


def create_app():
    app = Flask(__name__)
    app.config.from_mapping(
        DATABASE_HOST="db",  # Postgres 컨테이너의 이름을 사용
        DATABASE_NAME="postgres",
        DATABASE_USER="postgres",
        DATABASE_PASSWORD="mysecretpassword",
    )

    app.register_blueprint(api.bp)

    return app
