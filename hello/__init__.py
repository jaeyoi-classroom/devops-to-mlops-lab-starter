from flask import Flask

from . import api, db


def create_app():
    app = Flask(__name__)
    app.config.from_mapping(
        DATABASE_HOST="db",  # Postgres 컨테이너의 이름을 사용
        DATABASE_NAME="postgres",
        DATABASE_USER="postgres",
        DATABASE_PASSWORD="mysecretpassword",
    )

    with app.app_context():
        db.init_app(app)

    app.register_blueprint(api.bp)

    return app
