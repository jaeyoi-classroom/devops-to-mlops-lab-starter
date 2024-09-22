import psycopg2
from flask import current_app


def _get_db():
    return psycopg2.connect(
        database=current_app.config["DATABASE_NAME"],
        user=current_app.config["DATABASE_USER"],
        password=current_app.config["DATABASE_PASSWORD"],
        host=current_app.config["DATABASE_HOST"],
    )


def _init_db(db):
    with current_app.open_resource("schema.sql") as f:
        sql_script = f.read().decode("utf8")

    commands = sql_script.split(";")

    with db.cursor() as cursor:
        for command in commands:
            command = command.strip()
            if command:
                cursor.execute(command)
        db.commit()


def get_db_connection():
    db = _get_db()
    _init_db(db)
    return db
