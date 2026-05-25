from flask import Flask, jsonify, request
import os

app = Flask(__name__)

# In-memory storage (for demo)
tasks = [
    {"id": 1, "title": "Learn Flask", "done": True},
    {"id": 2, "title": "Build CI/CD Pipeline", "done": False},
]

@app.route("/")
def home():
    return jsonify({"message": "Welcome to Task Manager API"}), 200


@app.route("/tasks", methods=["GET"])
def get_tasks():
    return jsonify(tasks), 200


@app.route("/tasks", methods=["POST"])
def add_task():
    data = request.get_json()
    if not data or "title" not in data:
        return jsonify({"error": "Title is required"}), 400

    new_task = {
        "id": len(tasks) + 1,
        "title": data["title"],
        "done": False
    }
    tasks.append(new_task)
    return jsonify(new_task), 201


if __name__ == "__main__":
    debug_mode = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(debug=debug_mode)