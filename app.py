from flask import Flask, render_template, request, jsonify
from chatbot import get_response  # From your previous chatbot.py
import sqlite3
from datetime import datetime

app = Flask(__name__)

# Helper function to interact with the database
def execute_db_query(query, params=()):
    try:
        conn = sqlite3.connect('bank.db', timeout=10, check_same_thread=False)  # timeout to avoid locking
        c = conn.cursor()
        c.execute(query, params)
        conn.commit()
        conn.close()
    except sqlite3.OperationalError as e:
        print(f"[ERROR] Database operation failed: {e}")
        return False
    return True


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/get", methods=["POST"])
def chatbot_response():
    user_input = request.form["msg"]
    response = get_response(user_input)
    return jsonify({"response": response})

@app.route("/submit_feedback", methods=["POST"])
def submit_feedback():
    feedback_data = request.get_json()
    
    # Get the feedback data
    user_input = feedback_data.get("user_input")
    correct_intent = feedback_data.get("correct_intent")
    
    # Validate the feedback data
    if not user_input or not correct_intent:
        return jsonify({"message": "Invalid feedback data"}), 400

    # Get the current timestamp
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Insert the feedback data into the feedback table in the database
    query = """
        INSERT INTO feedback (user_input, correct_intent, timestamp)
        VALUES (?, ?, ?)
    """
    if execute_db_query(query, (user_input, correct_intent, timestamp)):
        return jsonify({"message": "Feedback submitted successfully!"})
    else:
        return jsonify({"message": "Failed to submit feedback, please try again later."}), 500
    

@app.route('/dashboard')
def dashboard():
    conn = sqlite3.connect('bank.db', timeout=10, check_same_thread=False)  # timeout to avoid locking
    feedbacks = conn.execute('SELECT * FROM feedback').fetchall()  # Assuming 'feedback' is your table
    conn.close()
    return render_template('dashboard.html', feedbacks=feedbacks)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
