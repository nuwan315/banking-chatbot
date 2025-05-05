import json
import sqlite3
from flask import Flask, render_template, request, jsonify
from chatbot import get_response  # from your previous chatbot.py

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/get", methods=["POST"])
def chatbot_response():
    user_input = request.form["msg"]
    response = get_response(user_input)
    return jsonify({"response": response})

@app.route("/feedback", methods=["POST"])
def save_feedback():
    data = request.get_json()
    user_message = data.get("user_message")
    bot_response = data.get("bot_response")
    feedback_type = data.get("feedback_type")

    try:
        conn = sqlite3.connect('bank.db')
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO feedback (user_message, bot_response, feedback_type)
            VALUES (?, ?, ?)
        """, (user_message, bot_response, feedback_type))
        conn.commit()
        conn.close()
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/tag_feedback", methods=["POST"])
def save_tagged_feedback():
    data = request.get_json()
    user_message = data.get("user_message")
    correct_tag = data.get("correct_tag")

    try:
        conn = sqlite3.connect('bank.db')
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO feedback (user_message, correct_tag)
            VALUES (?, ?)
        """, (user_message, correct_tag))
        conn.commit()
        conn.close()
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
