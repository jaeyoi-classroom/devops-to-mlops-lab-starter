import psycopg2
from flask import current_app, g


def get_db():
    if "db" not in g:
        g.db = psycopg2.connect(
            database=current_app.config["DATABASE_NAME"],
            user=current_app.config["DATABASE_USER"],
            password=current_app.config["DATABASE_PASSWORD"],
            host=current_app.config["DATABASE_HOST"],
        )
        g.db.autocommit = True

    return g.db


def close_db(e=None):
    db = g.pop("db", None)

    if db is not None:
        db.close()


def init_db():
    db = get_db()

    with current_app.open_resource("schema.sql") as f:
        sql_script = f.read().decode("utf8")

    commands = sql_script.split(";")

    with db.cursor() as cursor:
        for command in commands:
            command = command.strip()
            if command:
                cursor.execute(command)
        db.commit()


def init_app(app):
    app.teardown_appcontext(close_db)
    try:
        init_db()
    except:
        pass
