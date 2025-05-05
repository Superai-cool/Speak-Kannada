from flask import Flask, render_template, request, redirect, session, url_for, jsonify
import os
import re
from firebase_admin import db, credentials, initialize_app
from openai_handler import generate_kannada_translation
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")
app.permanent_session_lifetime = timedelta(days=7)

# Initialize Firebase
firebase_json = os.environ.get("FIREBASE_JSON")
firebase_cred = credentials.Certificate(eval(firebase_json))
initialize_app(firebase_cred, {
    'databaseURL': os.environ.get("FIREBASE_DB_URL")
})
users_ref = db.reference("users")

# Admin mobile number (ensure this matches Firebase DB entry)
ADMIN_MOBILE = "8830720742"

@app.route("/")
def index():
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login():
    name = request.form.get("name")
    mobile = request.form.get("mobile")
    password = request.form.get("password")

    users = users_ref.get()
    for uid, user in users.items():
        if user["mobile"] == mobile and user["password"] == password:
            session["name"] = user["name"]
            session["mobile"] = user["mobile"]
            session["credits"] = user["credits"]
            session["is_admin"] = (user["mobile"] == ADMIN_MOBILE)
            return redirect("/admin" if session["is_admin"] else "/dashboard")

    return render_template("login.html", error="Invalid credentials")

@app.route("/dashboard")
def dashboard():
    if "mobile" not in session:
        return redirect("/")
    return render_template("dashboard.html", name=session["name"], credits=session["credits"])

@app.route("/admin")
def admin_panel():
    if "mobile" not in session or session.get("mobile") != ADMIN_MOBILE:
        return redirect("/")
    users = users_ref.get()
    return render_template("admin.html", users=users)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/ask", methods=["POST"])
def ask():
    if "mobile" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    user_input = request.json.get("message")
    if not user_input or not re.search(r'[a-zA-Z]', user_input):
        return jsonify({"error": "Please ask your question in English only."}), 400

    if session.get("credits", 0) <= 0:
        return jsonify({"error": "No credits remaining."}), 402

    output = generate_kannada_translation(user_input)

    # Deduct credit
    user_key = None
    users = users_ref.get()
    for uid, user in users.items():
        if user["mobile"] == session["mobile"]:
            user_key = uid
            break

    if user_key:
        current_credits = users[user_key]["credits"]
        updated_credits = max(0, current_credits - 1)
        users_ref.child(user_key).update({"credits": updated_credits})
        session["credits"] = updated_credits

    return jsonify({"response": output, "credits": session["credits"]})

if __name__ == "__main__":
    app.run(debug=True)
