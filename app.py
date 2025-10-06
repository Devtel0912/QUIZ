from flask import Flask, jsonify, request
import json
import os


app = Flask(__name__)

quizzFolder = "quizzes"
userFile = "users"


def load_quiz():
    quizzes = []
    for file_name in os.listdir(quizzFolder):
        if file_name.endswith(".json"):
             with open(os.path.join(quizzFolder, file_name), "r") as f:
                quizzes.append(json.load(f))
    return quizzes


def loading():
    with open(userFile, "r") as f:
        return json.load(f)
    

def saving_users():
    with open(userFile, "w") as f:
        json.dump(userFile, f, indent=4)


@app.route("/quizzes", methods=["GET"])
def get_quizzes():
    quizzes = load_quiz()
    # Don't return answers
    for quiz in quizzes:
        for q in quiz["questions"]:
            q.pop("answer", None)
    return jsonify(quizzes)

# API: Submit quiz answers
@app.route("/quizzes/<int:quiz_id>/submit", methods=["POST"])
def submit_quiz(quiz_id):
    data = request.json
    user_id = data.get("user_id")
    answers = data.get("answers", [])

    quizzes = load_quiz()
    quiz = next((q for q in quizzes if q["quiz_id"] == quiz_id), None)
    if not quiz:
        return jsonify({"error": "Quiz not found"}), 404

    score = 0
    for q in quiz["questions"]:
        user_ans = next((a["answer"] for a in answers if a["question_id"] == q["question_id"]), None)
        if user_ans == q["answer"]:
            score += 1

    # Save user attempt
    users = loading()
    user = next((u for u in users if u["user_id"] == user_id), None)
    if not user:
        user = {"user_id": user_id, "attempts": []}
        users.append(user)
    user["attempts"].append({"quiz_id": quiz_id, "score": score})
    saving_users(users)

    return jsonify({"score": score, "total": len(quiz["questions"])})

# API: Register user
@app.route("/users/register", methods=["POST"])
def register_user():
    data = request.json
    user_id = data.get("user_id")
    users = loading()
    if any(u["user_id"] == user_id for u in users):
        return jsonify({"error": "User already exists"}), 400
    users.append({"user_id": user_id, "attempts": []})
    saving_users(users)
    return jsonify({"message": "User registered successfully"})

if __name__ == "__main__":
    app.run(debug=True)