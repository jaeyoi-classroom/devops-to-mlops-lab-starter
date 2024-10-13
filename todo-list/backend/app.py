from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)

# PostgreSQL 데이터베이스 설정
app.config["SQLALCHEMY_DATABASE_URI"] = (
    "postgresql://postgres:mysecretpassword@db/todo_list"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# TODO 모델 정의
class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Boolean, default=False)


# 데이터베이스 초기화
with app.app_context():
    db.create_all()


# REST API 엔드포인트
@app.route("/api/todos", methods=["GET", "POST"])
def manage_todos():
    if request.method == "POST":
        # 새로운 TODO 추가
        task_data = request.json.get("task", "")
        if task_data:
            new_todo = Todo(task=task_data)
            db.session.add(new_todo)
            try:
                db.session.commit()
                return jsonify(
                    {
                        "message": "Task added",
                        "todo": {
                            "id": new_todo.id,
                            "task": new_todo.task,
                            "completed": new_todo.completed,
                        },
                    }
                ), 201
            except IntegrityError:
                db.session.rollback()
                return jsonify({"message": "Error adding task"}), 400
        return jsonify({"message": "No task provided"}), 400

    # 모든 TODO 리스트 가져오기
    todos = Todo.query.all()
    return jsonify(
        [
            {"id": todo.id, "task": todo.task, "completed": todo.completed}
            for todo in todos
        ]
    )


@app.route("/api/todos/<int:todo_id>", methods=["PUT"])
def update_todo(todo_id):
    todo = Todo.query.get(todo_id)

    if not todo:
        return jsonify({"message": "Task not found"}), 404

    # TODO 완료 상태 업데이트
    todo.completed = request.json.get("completed", todo.completed)
    db.session.commit()
    return jsonify(
        {
            "message": "Task updated",
            "todo": {"id": todo.id, "task": todo.task, "completed": todo.completed},
        }
    )


@app.route("/api/todos/<int:todo_id>", methods=["DELETE"])
def delete_todo(todo_id):
    todo = Todo.query.get(todo_id)

    if not todo:
        return jsonify({"message": "Task not found"}), 404

    db.session.delete(todo)
    db.session.commit()
    return jsonify({"message": "Task deleted"})


if __name__ == "__main__":
    app.run(debug=True)
