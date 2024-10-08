from flask import Blueprint

from .db import get_db_connection

bp = Blueprint("api", __name__)


@bp.route("/")
def hello():
    return "Hello, DevOps!"


@bp.route("/visit")
def visit():
    with get_db_connection() as db:
        with db.cursor() as cursor:
            cursor.execute("""
                UPDATE visit_count 
                SET count = count + 1 
                WHERE id = 1
                RETURNING count;
            """)
            count = cursor.fetchone()[0]
            db.commit()

    return f"{count}번째 방문입니다."
