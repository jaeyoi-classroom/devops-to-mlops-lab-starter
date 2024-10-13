from flask import Blueprint, jsonify
from prometheus_client import Counter, generate_latest

from .db import get_db_connection

bp = Blueprint("api", __name__)


@bp.route("/")
def hello():
    REQUEST_COUNT.labels(endpoint="/").inc()
    return "Hello, DevOps!!"


@bp.route("/visit")
def visit():
    REQUEST_COUNT.labels(endpoint="/visit").inc()

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


# Prometheus 메트릭 설정
REQUEST_COUNT = Counter("app_requests_total", "Total number of requests", ["endpoint"])


@bp.route("/metrics")
def metrics():
    return generate_latest()


@bp.route("/healthcheck", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy"}), 200
